import pytest
from modules.planner import SearchStrategySelector, SearchStrategy

@pytest.fixture
def selector():
    return SearchStrategySelector()

def test_select_keyword_strategy(selector):
    query = "Who is Albert Einstein?"
    strategy = selector.select_strategy(query)

    assert strategy == SearchStrategy.KEYWORD or strategy == SearchStrategy.SEMANTIC

def test_select_semantic_strategy(selector):
    query = "What is the meaning of artificial intelligence?"
    strategy = selector.select_strategy(query)

    assert strategy in [SearchStrategy.SEMANTIC, SearchStrategy.KEYWORD]

def test_select_hybrid_strategy_for_complex(selector):
    query = "Compare machine learning and deep learning, and explain their differences"
    strategy = selector.select_strategy(query)

    assert strategy in [SearchStrategy.HYBRID, SearchStrategy.SEMANTIC]

def test_select_dense_passage_strategy(selector):
    query = "Summarize the article about climate change"
    strategy = selector.select_strategy(query)

    assert strategy in [SearchStrategy.DENSE_PASSAGE, SearchStrategy.SEMANTIC]

def test_get_retrieval_params_semantic(selector):
    strategy = SearchStrategy.SEMANTIC
    params = selector.get_retrieval_params(strategy)

    assert params["strategy"] == "semantic"
    assert "top_k" in params
    assert "score_threshold" in params
    assert params["use_embeddings"] == True

def test_get_retrieval_params_keyword(selector):
    strategy = SearchStrategy.KEYWORD
    params = selector.get_retrieval_params(strategy)

    assert params["strategy"] == "keyword"
    assert params["use_bm25"] == True
    assert params["top_k"] > 5

def test_get_retrieval_params_hybrid(selector):
    strategy = SearchStrategy.HYBRID
    params = selector.get_retrieval_params(strategy)

    assert params["strategy"] == "hybrid"
    assert params["use_embeddings"] == True
    assert params["use_bm25"] == True
    assert "semantic_weight" in params
    assert "keyword_weight" in params

def test_keyword_heavy_detection(selector):
    query = "Who is the president of France?"
    is_keyword = selector._is_keyword_heavy_query(query)

    assert is_keyword == True

def test_complex_query_detection(selector):
    query = "What is AI, and how is it different from ML, and what are the applications?"
    is_complex = selector._is_complex_query(query)

    assert is_complex == True

def test_dense_passage_detection(selector):
    query = "Explain the theory of relativity"
    is_dense = selector._is_dense_passage_query(query)

    assert is_dense == True

def test_strategy_explanation(selector):
    query = "What is Python?"
    strategy = selector.select_strategy(query)
    explanation = selector.explain_strategy(query, strategy)

    assert explanation != ""
    assert isinstance(explanation, str)
