"""Context Router tests (Asset Context Map)."""

from quantumfinance.context.router import get_context_keywords, route_context_search


def test_get_context_keywords_returns_spheres_for_known_ticker():
    """Validates that the known ticker's spheres and keywords are returned."""
    result = get_context_keywords("PETR4")
    assert "energy" in result
    assert "politics_regulation" in result
    assert len(result["energy"]) > 0


def test_get_context_keywords_returns_empty_for_unknown_ticker():
    """Validates that a ticker outside the Asset Context Map returns an empty dict."""
    result = get_context_keywords("TICKER_INEXISTENTE")
    assert result == {}


def test_route_context_search_classifies_news():
    """Validates that news is classified into the correct sphere by keyword match."""
    news = [
        {"title": "Petrobras anuncia nova política de preços de combustíveis", "summary": ""},
        {"title": "OPEP reduz produção de petróleo Brent sobe", "summary": ""},
    ]
    result = route_context_search("PETR4", news)
    assert "politics_regulation" in result or "energy" in result
