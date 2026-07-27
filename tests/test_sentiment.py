"""Sentiment pipeline tests."""

from quantumfinance.features.sentiment import aggregate_sentiment, classify_sentiment


def test_classify_sentiment_returns_valid_label():
    """Validates that classification returns one of the three expected labels."""
    result = classify_sentiment("A empresa teve excelentes resultados no trimestre")
    assert result["label"] in ("POSITIVO", "NEGATIVO", "NEUTRO")


def test_classify_sentiment_scores_sum_to_one():
    """Validates that the probability scores sum to approximately 1."""
    result = classify_sentiment("O mercado reagiu com cautela à notícia")
    total = sum(result["scores"].values())
    assert abs(total - 1.0) < 0.01


def test_aggregate_sentiment_empty_list():
    """Validates that an empty news list does not break aggregation."""
    result = aggregate_sentiment([])
    assert result["sentiment_label"] == "NEUTRO"
    assert result["news_count"] == 0
    assert result["top_headlines"] == []


def test_aggregate_sentiment_has_required_keys():
    """Validates that the aggregated output contains all required keys."""
    news = [{"title": "Empresa anuncia recorde de lucros", "summary": "Resultado positivo no trimestre"}]
    result = aggregate_sentiment(news)
    required_keys = {"sentiment_score", "sentiment_label", "news_count", "top_headlines"}
    assert required_keys.issubset(result.keys())


def test_sentiment_score_in_valid_range():
    """Validates that the aggregated score is always between 0 and 1."""
    news = [{"title": "Notícia neutra sobre o mercado", "summary": ""}]
    result = aggregate_sentiment(news)
    assert 0.0 <= result["sentiment_score"] <= 1.0


def test_classify_sentiment_correct_polarity():
    """Validates that clearly positive and negative sentences receive the correct label.

    Protects against regression of the FinBERT-PT-BR model-label mapping bug,
    where the model's id2label (POSITIVE/NEGATIVE/NEUTRAL) was initially
    associated with the Portuguese labels in the wrong order.
    """
    positive_result = classify_sentiment(
        "A empresa anunciou lucro recorde e forte crescimento no trimestre"
    )
    assert positive_result["label"] == "POSITIVO", (
        f"Esperado POSITIVO, obtido {positive_result['label']} "
        f"com scores {positive_result['scores']}"
    )

    negative_result = classify_sentiment(
        "A empresa anunciou prejuízo recorde e forte queda nas ações"
    )
    assert negative_result["label"] == "NEGATIVO", (
        f"Esperado NEGATIVO, obtido {negative_result['label']} "
        f"com scores {negative_result['scores']}"
    )
