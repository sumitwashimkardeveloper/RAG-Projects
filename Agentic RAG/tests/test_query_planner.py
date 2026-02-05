import pytest
from modules.planner import QueryPlanner

@pytest.fixture
def planner(config):
    return QueryPlanner(config)

def test_planner_initialization(planner):
    assert planner.intent_classifier is not None
    assert planner.query_analyzer is not None
    assert planner.strategy_selector is not None
    assert planner.plan_generator is not None

def test_plan_query_basic(planner):
    query = "What is machine learning?"
    plan = planner.plan(query)

    assert plan.original_query == query
    assert plan.intent != ""
    assert plan.search_strategy != ""
    assert plan.retrieval_plan is not None

def test_plan_includes_sub_queries(planner):
    query = "What is AI and how does it work?"
    plan = planner.plan(query)

    assert "sub_queries" in dir(plan) or hasattr(plan, "sub_queries")

def test_classify_intent(planner):
    query = "What is Python?"
    intent, confidence = planner.classify_intent(query)

    assert intent != ""
    assert 0 <= confidence <= 1

def test_select_search_strategy(planner):
    query = "Find information about machine learning"
    strategy, params = planner.select_search_strategy(query)

    assert strategy != ""
    assert "top_k" in params
    assert "score_threshold" in params

def test_analyze_query(planner):
    query = "How to learn Python programming?"
    analysis = planner.analyze_query(query)

    assert "keywords" in analysis
    assert "entities" in analysis
    assert "complexity" in analysis

def test_get_intent_features(planner):
    query = "Summarize this article about AI"
    features = planner.get_intent_features(query)

    assert "intent" in features
    assert "confidence" in features
    assert "is_question" in features
    assert "word_count" in features

def test_get_plan_steps(planner):
    query = "What is machine learning?"
    plan = planner.plan(query)
    steps = planner.get_plan_steps(plan)

    assert isinstance(steps, list)
    assert len(steps) > 0
    assert all("step" in step for step in steps)
    assert all("action" in step for step in steps)

def test_explain_plan(planner):
    query = "What is artificial intelligence?"
    plan = planner.plan(query)
    explanation = planner.explain_plan(plan)

    assert query in explanation
    assert plan.intent in explanation
    assert plan.search_strategy in explanation

def test_plan_with_complex_query(planner):
    query = "Compare Python, JavaScript, and Go in terms of performance, ease of learning, and community support"
    plan = planner.plan(query)

    assert len(plan.sub_queries) > 0 or plan.metadata.get("complexity", 0) > 0.5

def test_plan_metadata_included(planner):
    query = "What is cloud computing?"
    plan = planner.plan(query)

    assert plan.metadata is not None
    assert "intent_confidence" in plan.metadata
    assert "complexity" in plan.metadata
    assert "keywords" in plan.metadata

def test_multiple_queries_independent(planner):
    query1 = "What is AI?"
    query2 = "How to learn programming?"

    plan1 = planner.plan(query1)
    plan2 = planner.plan(query2)

    assert plan1.intent != plan2.intent
    assert plan1.original_query != plan2.original_query
