import pytest
from modules.planner import PlanGenerator, PlanStep, RetrievalPlan

@pytest.fixture
def generator():
    return PlanGenerator()

@pytest.fixture
def sample_analysis():
    return {
        "complexity": 0.5,
        "sub_queries": [{"text": "sub1"}, {"text": "sub2"}],
        "has_multiple_parts": True
    }

def test_generate_plan_basic(generator, sample_analysis):
    query = "What is machine learning?"
    plan = generator.generate_plan(query, sample_analysis, "semantic")

    assert plan.query == query
    assert len(plan.steps) > 0
    assert plan.total_estimated_cost > 0

def test_generate_plan_has_required_steps(generator, sample_analysis):
    query = "What is AI?"
    plan = generator.generate_plan(query, sample_analysis, "semantic")

    actions = {step.action for step in plan.steps}
    assert "parse_query" in actions
    assert "retrieve_documents" in actions
    assert "aggregate_results" in actions

def test_plan_respects_max_steps(generator, sample_analysis):
    query = "Complex query with many parts"
    plan = generator.generate_plan(query, sample_analysis, "hybrid")
    optimized = generator.optimize_plan(plan)

    assert len(optimized.steps) <= generator.max_steps

def test_plan_steps_have_dependencies(generator, sample_analysis):
    query = "Test query"
    plan = generator.generate_plan(query, sample_analysis, "semantic")

    first_step = [s for s in plan.steps if s.step_number == 1][0]
    assert len(first_step.dependencies) == 0

def test_validate_plan_success(generator, sample_analysis):
    query = "Valid query"
    plan = generator.generate_plan(query, sample_analysis, "semantic")
    validation = generator.validate_plan(plan)

    assert "is_valid" in validation
    assert "issues" in validation

def test_plan_complexity_increases_steps(generator):
    simple_analysis = {
        "complexity": 0.2,
        "sub_queries": [],
        "has_multiple_parts": False
    }

    complex_analysis = {
        "complexity": 0.8,
        "sub_queries": [{"text": f"sub{i}"} for i in range(3)],
        "has_multiple_parts": True
    }

    simple_plan = generator.generate_plan("Simple", simple_analysis, "semantic")
    complex_plan = generator.generate_plan("Complex", complex_analysis, "semantic")

    assert len(complex_plan.steps) >= len(simple_plan.steps)

def test_plan_with_multiple_sub_queries(generator):
    analysis = {
        "complexity": 0.6,
        "sub_queries": [{"text": f"sub{i}"} for i in range(4)],
        "has_multiple_parts": True
    }

    plan = generator.generate_plan("Multi-part query", analysis, "hybrid")
    actions = [step.action for step in plan.steps]

    assert "process_sub_queries" in actions

def test_plan_metadata(generator, sample_analysis):
    query = "Test query"
    plan = generator.generate_plan(query, sample_analysis, "semantic")

    assert "complexity" in plan.metadata
    assert "sub_query_count" in plan.metadata
    assert "strategy" in plan.metadata
