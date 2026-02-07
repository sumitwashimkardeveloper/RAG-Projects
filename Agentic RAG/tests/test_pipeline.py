import pytest
from unittest.mock import Mock, MagicMock, patch
from pipeline import AgenticRAGPipeline, PipelineState

@pytest.fixture
def mock_components():
    components = {
        "planner": Mock(),
        "retriever": Mock(),
        "critic": Mock(),
        "query_rewriter": Mock(),
        "answer_generator": Mock()
    }
    return components

@pytest.fixture
def pipeline(config, mock_components):
    pipeline = AgenticRAGPipeline(config)

    pipeline.planner = mock_components["planner"]
    pipeline.retriever = mock_components["retriever"]
    pipeline.critic = mock_components["critic"]
    pipeline.query_rewriter = mock_components["query_rewriter"]
    pipeline.answer_generator = mock_components["answer_generator"]

    return pipeline

def test_pipeline_initialization(config):
    pipeline = AgenticRAGPipeline(config)

    assert pipeline.state_machine is not None
    assert pipeline.iteration_controller is not None
    assert pipeline.result_accumulator is not None

def test_pipeline_state_creation():
    state = PipelineState(query="test query")

    assert state.query == "test query"
    assert state.current_query == ""
    assert state.iteration == 0

def test_pipeline_process(pipeline):
    with patch.object(pipeline, 'execute_pipeline', return_value={"success": True}):
        result = pipeline.process("test query")

        assert result is not None

def test_pipeline_state_reset(pipeline):
    pipeline.state_machine.move_to_phase(pipeline.state_machine.current_phase)
    initial_history_len = len(pipeline.state_machine.get_state_history())

    pipeline.state_machine.reset()

    assert pipeline.state_machine.current_phase.value == "planner"

def test_should_continue_iteration(pipeline):
    feedback = {
        "should_continue": True,
        "gaps_identified": ["gap1"]
    }

    should_continue = pipeline.should_continue_iteration(feedback, 1)

    assert isinstance(should_continue, bool)

def test_accumulate_results(pipeline):
    documents = [
        {
            "id": "doc1",
            "score": 0.9,
            "metadata": {"content": "test", "source": "test.com"}
        }
    ]

    pipeline.accumulate_results(documents, 1)

    accumulated = pipeline.result_accumulator.get_accumulated_results()
    assert len(accumulated) >= 1

def test_get_pipeline_statistics(pipeline):
    stats = pipeline.get_pipeline_statistics()

    assert "iteration_metrics" in stats
    assert "accumulator_stats" in stats
    assert "state_history" in stats

def test_build_result_success(pipeline):
    state = PipelineState(
        query="test query",
        answer="test answer",
        documents=[{"id": "doc1"}]
    )

    pipeline.state_machine.move_to_phase(pipeline.state_machine.__class__.__dict__.get("COMPLETE", None) or
                                         next(p for p in pipeline.state_machine.__class__.__dict__.values()
                                              if hasattr(p, 'value') and p.value == "complete"))

    state.metadata["test"] = "data"

    result = pipeline._build_result(state)

    assert "success" in result
    assert "answer" in result

def test_error_handling(pipeline):
    with patch.object(pipeline, 'execute_pipeline', side_effect=Exception("Test error")):
        result = pipeline.process("test query")

        assert result["success"] == False
        assert "error" in result

def test_pipeline_flow(pipeline):
    assert pipeline.state_machine.current_phase.value == "planner"
    assert pipeline.iteration_controller.current_iteration == 0
    assert len(pipeline.result_accumulator.accumulated) == 0
