from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from modules.utils import (
    get_logger, get_config, StateMachine, IterationController,
    ResultAccumulator, PipelinePhase
)
from modules import QueryPlanner, Retriever, Critic, QueryRewriter, AnswerGenerator

logger = get_logger(__name__)

@dataclass
class PipelineState:
    query: str
    current_query: str = ""
    iteration: int = 0
    documents: List = field(default_factory=list)
    accumulated_documents: List = field(default_factory=list)
    feedback: Dict[str, Any] = field(default_factory=dict)
    answer: Optional[str] = None
    query_plan: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class AgenticRAGPipeline:
    def __init__(self, config=None):
        self.config = config or get_config()
        self.logger = get_logger(__name__)

        self.planner = QueryPlanner(self.config)
        self.retriever = Retriever(self.config)
        self.critic = Critic(self.config)
        self.query_rewriter = QueryRewriter(self.config)
        self.answer_generator = AnswerGenerator(self.config)

        self.state_machine = StateMachine()
        self.iteration_controller = IterationController(
            max_iterations=self.config.get("loop.max_iterations", 5),
            timeout_seconds=self.config.get("loop.iteration_timeout", 60)
        )
        self.result_accumulator = ResultAccumulator(
            max_documents=self.config.get("retriever.max_accumulated", 50)
        )

    def process(self, query: str) -> Dict[str, Any]:
        self.logger.info(f"Starting pipeline for query: {query[:100]}")

        state = PipelineState(query=query, current_query=query)
        self.state_machine.reset()
        self.iteration_controller.reset()
        self.result_accumulator.clear()

        try:
            result = self.execute_pipeline(state)
            return result
        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            self.state_machine.set_error_phase(str(e))
            return {
                "success": False,
                "error": str(e),
                "phase": self.state_machine.current_phase.value
            }

    def execute_pipeline(self, state: PipelineState) -> Dict[str, Any]:
        while not self.state_machine.is_terminal_phase():
            current_phase = self.state_machine.get_current_phase()

            if current_phase == PipelinePhase.PLANNER:
                state = self._execute_planner(state)
            elif current_phase == PipelinePhase.RETRIEVER:
                state = self._execute_retriever(state)
            elif current_phase == PipelinePhase.CRITIC:
                state = self._execute_critic(state)
            elif current_phase == PipelinePhase.QUERY_REWRITER:
                state = self._execute_query_rewriter(state)
            elif current_phase == PipelinePhase.ANSWER_GENERATOR:
                state = self._execute_answer_generator(state)

            next_phase = self.state_machine.evaluate_transitions(state.metadata)
            if next_phase:
                self.state_machine.move_to_phase(next_phase)
            else:
                self.logger.warning(f"No transition available from {current_phase.value}")
                break

        return self._build_result(state)

    def _execute_planner(self, state: PipelineState) -> PipelineState:
        self.logger.info("Executing planner phase")
        self.iteration_controller.start_iteration()

        query_plan = self.planner.plan(state.current_query)
        state.query_plan = {
            "intent": query_plan.intent,
            "strategy": query_plan.search_strategy,
            "sub_queries": query_plan.sub_queries
        }
        state.metadata["query_plan"] = state.query_plan

        self.iteration_controller.end_iteration({
            "phase": "planner",
            "confidence_score": 0.0
        })

        return state

    def _execute_retriever(self, state: PipelineState) -> PipelineState:
        self.logger.info(f"Executing retriever phase (iteration {state.iteration + 1})")

        strategy = state.query_plan.get("strategy", "hybrid") if state.query_plan else "hybrid"
        retrieval_result = self.retriever.retrieve(state.current_query, strategy=strategy)

        state.documents = [
            {
                "id": doc.source,
                "content": doc.content,
                "score": doc.relevance_score,
                "metadata": {
                    "content": doc.content,
                    "source": doc.source,
                    "rank": doc.rank
                }
            }
            for doc in retrieval_result.documents
        ]

        self.result_accumulator.add_results(state.documents, state.iteration + 1)
        state.accumulated_documents = self.result_accumulator.get_accumulated_results()

        state.metadata["retrieval_result"] = {
            "strategy": strategy,
            "documents_retrieved": len(state.documents)
        }

        self.iteration_controller.end_iteration({
            "phase": "retriever",
            "documents_retrieved": len(state.documents),
            "confidence_score": 0.0
        })

        return state

    def _execute_critic(self, state: PipelineState) -> PipelineState:
        self.logger.info("Executing critic phase")

        feedback = self.critic.evaluate(state.current_query, state.documents)

        state.feedback = {
            "is_relevant": feedback.is_relevant,
            "confidence_score": feedback.confidence_score,
            "gaps_identified": feedback.gaps_identified,
            "completeness_score": feedback.completeness_score,
            "should_continue": self.iteration_controller.should_continue({
                "should_continue": feedback.should_continue,
                "gaps_identified": feedback.gaps_identified
            })
        }

        state.metadata.update(state.feedback)

        self.iteration_controller.end_iteration({
            "phase": "critic",
            "confidence_score": feedback.confidence_score,
            "gaps_identified": feedback.gaps_identified
        })

        return state

    def _execute_query_rewriter(self, state: PipelineState) -> PipelineState:
        self.logger.info("Executing query rewriter phase")

        rewritten = self.query_rewriter.rewrite(state.current_query, feedback=state.feedback)

        state.current_query = rewritten.rewritten_query
        state.iteration += 1

        state.metadata["query_rewritten"] = {
            "strategy": rewritten.strategy,
            "new_query": rewritten.rewritten_query,
            "alternatives": rewritten.alternatives
        }

        self.iteration_controller.end_iteration({
            "phase": "query_rewriter",
            "confidence_score": rewritten.confidence_score
        })

        return state

    def _execute_answer_generator(self, state: PipelineState) -> PipelineState:
        self.logger.info("Executing answer generator phase")

        answer_result = self.answer_generator.generate(
            state.query,
            state.accumulated_documents,
            context=state.metadata
        )

        state.answer = answer_result.answer
        state.metadata["answer"] = {
            "content": answer_result.answer,
            "confidence": answer_result.confidence_score,
            "citations": [
                {"source": c.source, "snippet": c.content_snippet}
                for c in answer_result.citations
            ]
        }

        self.iteration_controller.end_iteration({
            "phase": "answer_generator",
            "confidence_score": answer_result.confidence_score
        })

        return state

    def _build_result(self, state: PipelineState) -> Dict[str, Any]:
        is_complete = self.state_machine.current_phase == PipelinePhase.COMPLETE
        summary = self.iteration_controller.get_summary()
        accumulator_summary = self.result_accumulator.get_summary()

        return {
            "success": is_complete,
            "original_query": state.query,
            "answer": state.answer,
            "documents": state.accumulated_documents,
            "feedback": state.feedback,
            "iterations": summary,
            "accumulator": accumulator_summary,
            "phase": self.state_machine.current_phase.value,
            "state_history": [p.value for p in self.state_machine.get_state_history()]
        }

    def should_continue_iteration(self, feedback: Dict[str, Any], iteration: int) -> bool:
        return self.iteration_controller.should_continue(feedback)

    def accumulate_results(self, documents: List, iteration: int) -> None:
        self.result_accumulator.add_results(documents, iteration)

    def get_pipeline_statistics(self) -> Dict[str, Any]:
        return {
            "iteration_metrics": self.iteration_controller.get_summary(),
            "accumulator_stats": self.result_accumulator.get_summary(),
            "state_history": [p.value for p in self.state_machine.get_state_history()]
        }
