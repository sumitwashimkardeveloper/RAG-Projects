from typing import Dict, Any, Callable, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from modules.utils import get_logger

logger = get_logger(__name__)

class PipelinePhase(Enum):
    PLANNER = "planner"
    RETRIEVER = "retriever"
    CRITIC = "critic"
    QUERY_REWRITER = "query_rewriter"
    ANSWER_GENERATOR = "answer_generator"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class StateTransition:
    from_phase: PipelinePhase
    to_phase: PipelinePhase
    condition: Callable[[Dict[str, Any]], bool]
    action: Optional[Callable] = None

class StateMachine:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.current_phase = PipelinePhase.PLANNER
        self.previous_phase = None
        self.transitions: Dict[PipelinePhase, List[StateTransition]] = {}
        self.state_history: List[PipelinePhase] = [PipelinePhase.PLANNER]
        self._initialize_default_transitions()

    def _initialize_default_transitions(self):
        self.add_transition(
            PipelinePhase.PLANNER,
            PipelinePhase.RETRIEVER,
            lambda state: "query_plan" in state
        )

        self.add_transition(
            PipelinePhase.RETRIEVER,
            PipelinePhase.CRITIC,
            lambda state: "retrieval_result" in state
        )

        self.add_transition(
            PipelinePhase.CRITIC,
            PipelinePhase.QUERY_REWRITER,
            lambda state: state.get("should_continue", False) and state.get("iteration", 0) < 5
        )

        self.add_transition(
            PipelinePhase.CRITIC,
            PipelinePhase.ANSWER_GENERATOR,
            lambda state: not state.get("should_continue", False)
        )

        self.add_transition(
            PipelinePhase.QUERY_REWRITER,
            PipelinePhase.RETRIEVER,
            lambda state: "rewritten_query" in state
        )

        self.add_transition(
            PipelinePhase.ANSWER_GENERATOR,
            PipelinePhase.COMPLETE,
            lambda state: "answer" in state
        )

    def add_transition(self,
                      from_phase: PipelinePhase,
                      to_phase: PipelinePhase,
                      condition: Callable,
                      action: Optional[Callable] = None):
        if from_phase not in self.transitions:
            self.transitions[from_phase] = []

        transition = StateTransition(from_phase, to_phase, condition, action)
        self.transitions[from_phase].append(transition)
        self.logger.info(f"Added transition: {from_phase.value} -> {to_phase.value}")

    def evaluate_transitions(self, state: Dict[str, Any]) -> Optional[PipelinePhase]:
        if self.current_phase not in self.transitions:
            return None

        for transition in self.transitions[self.current_phase]:
            try:
                if transition.condition(state):
                    if transition.action:
                        transition.action()

                    next_phase = transition.to_phase
                    self.logger.info(f"Transitioning: {self.current_phase.value} -> {next_phase.value}")
                    return next_phase
            except Exception as e:
                self.logger.warning(f"Error evaluating transition: {e}")

        return None

    def move_to_phase(self, phase: PipelinePhase):
        if phase != self.current_phase:
            self.previous_phase = self.current_phase
            self.current_phase = phase
            self.state_history.append(phase)
            self.logger.info(f"Moved to phase: {phase.value}")

    def get_current_phase(self) -> PipelinePhase:
        return self.current_phase

    def get_previous_phase(self) -> Optional[PipelinePhase]:
        return self.previous_phase

    def get_state_history(self) -> List[PipelinePhase]:
        return self.state_history

    def reset(self):
        self.current_phase = PipelinePhase.PLANNER
        self.previous_phase = None
        self.state_history = [PipelinePhase.PLANNER]
        self.logger.info("State machine reset")

    def is_terminal_phase(self) -> bool:
        return self.current_phase in [PipelinePhase.COMPLETE, PipelinePhase.ERROR]

    def set_error_phase(self, error_msg: str = ""):
        self.logger.error(f"Entering error phase: {error_msg}")
        self.move_to_phase(PipelinePhase.ERROR)
