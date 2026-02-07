import pytest
from modules.utils import StateMachine, PipelinePhase

@pytest.fixture
def state_machine():
    return StateMachine()

def test_initialization(state_machine):
    assert state_machine.current_phase == PipelinePhase.PLANNER
    assert state_machine.previous_phase is None

def test_add_transition(state_machine):
    state_machine.add_transition(
        PipelinePhase.PLANNER,
        PipelinePhase.RETRIEVER,
        lambda state: "test" in state
    )

    assert PipelinePhase.PLANNER in state_machine.transitions

def test_evaluate_transitions_no_condition(state_machine):
    next_phase = state_machine.evaluate_transitions({})

    assert next_phase is None or isinstance(next_phase, PipelinePhase)

def test_evaluate_transitions_with_condition(state_machine):
    state_machine.add_transition(
        PipelinePhase.PLANNER,
        PipelinePhase.RETRIEVER,
        lambda state: "query_plan" in state
    )

    state = {"query_plan": "test"}
    next_phase = state_machine.evaluate_transitions(state)

    assert next_phase == PipelinePhase.RETRIEVER

def test_move_to_phase(state_machine):
    state_machine.move_to_phase(PipelinePhase.RETRIEVER)

    assert state_machine.current_phase == PipelinePhase.RETRIEVER
    assert state_machine.previous_phase == PipelinePhase.PLANNER

def test_get_state_history(state_machine):
    state_machine.move_to_phase(PipelinePhase.RETRIEVER)
    state_machine.move_to_phase(PipelinePhase.CRITIC)

    history = state_machine.get_state_history()

    assert PipelinePhase.PLANNER in history
    assert PipelinePhase.RETRIEVER in history
    assert PipelinePhase.CRITIC in history

def test_reset(state_machine):
    state_machine.move_to_phase(PipelinePhase.RETRIEVER)
    state_machine.reset()

    assert state_machine.current_phase == PipelinePhase.PLANNER
    assert state_machine.previous_phase is None
    assert len(state_machine.get_state_history()) == 1

def test_is_terminal_phase(state_machine):
    assert not state_machine.is_terminal_phase()

    state_machine.move_to_phase(PipelinePhase.COMPLETE)
    assert state_machine.is_terminal_phase()

def test_set_error_phase(state_machine):
    state_machine.set_error_phase("Test error")

    assert state_machine.current_phase == PipelinePhase.ERROR
    assert state_machine.is_terminal_phase()

def test_default_transitions(state_machine):
    assert PipelinePhase.PLANNER in state_machine.transitions
    assert PipelinePhase.RETRIEVER in state_machine.transitions
    assert PipelinePhase.CRITIC in state_machine.transitions
