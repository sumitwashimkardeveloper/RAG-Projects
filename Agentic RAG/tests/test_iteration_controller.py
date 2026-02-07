import pytest
import time
from modules.utils import IterationController

@pytest.fixture
def controller():
    return IterationController(max_iterations=5, timeout_seconds=10)

def test_initialization(controller):
    assert controller.current_iteration == 0
    assert controller.max_iterations == 5
    assert controller.timeout_seconds == 10

def test_start_iteration(controller):
    controller.start_iteration()

    assert controller.current_iteration == 1

def test_multiple_iterations(controller):
    for i in range(3):
        controller.start_iteration()

    assert controller.current_iteration == 3

def test_should_continue_at_max(controller):
    controller.current_iteration = 5
    should_continue = controller.should_continue({})

    assert should_continue == False

def test_should_continue_with_gaps(controller):
    controller.start_iteration()
    should_continue = controller.should_continue({
        "should_continue": True,
        "gaps_identified": ["gap1", "gap2"]
    })

    assert should_continue == True

def test_should_continue_no_gaps(controller):
    controller.start_iteration()
    should_continue = controller.should_continue({
        "should_continue": True,
        "gaps_identified": []
    })

    assert should_continue == False

def test_get_elapsed_time(controller):
    controller.start_iteration()
    time.sleep(0.1)

    elapsed = controller.get_elapsed_time()

    assert elapsed >= 0.1

def test_get_iteration_metrics(controller):
    controller.start_iteration()
    controller.end_iteration({"confidence_score": 0.8})

    metrics = controller.get_iteration_metrics()

    assert metrics.iteration_count == 1
    assert metrics.current_confidence > 0

def test_end_iteration(controller):
    controller.start_iteration()
    controller.end_iteration({"test": "data"})

    assert len(controller.iteration_history) == 1

def test_get_iteration_history(controller):
    controller.start_iteration()
    controller.end_iteration({"confidence_score": 0.8})

    history = controller.get_iteration_history()

    assert len(history) == 1
    assert history[0]["iteration"] == 1

def test_reset(controller):
    controller.start_iteration()
    controller.end_iteration({})
    controller.reset()

    assert controller.current_iteration == 0
    assert len(controller.iteration_history) == 0

def test_get_summary(controller):
    controller.start_iteration()
    controller.end_iteration({"confidence_score": 0.7})

    summary = controller.get_summary()

    assert "total_iterations" in summary
    assert "total_time" in summary
    assert "avg_confidence" in summary
