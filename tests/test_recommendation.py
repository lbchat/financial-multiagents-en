"""Tests for the structured recommendation output model."""

import pytest
from pydantic import ValidationError

from quantumfinance.agents.decision_agent import Recommendation, RecommendationOutput

VALID_FIELDS = {
    "ticker": "PETR4",
    "date": "2026-06-20",
    "recommendation": Recommendation.COMPRAR,
    "confidence": 0.8,
    "rsi": 28.5,
    "macd_signal": "bullish",
    "sentiment_score": 0.7,
    "sentiment_label": "POSITIVO",
    "top_headlines": ["Petrobras anuncia lucro recorde"],
    "reasoning": "RSI em sobrevenda e sentimento positivo.",
}


def test_recommendation_accepts_only_valid_values():
    """Validates that Recommendation accepts only COMPRAR, VENDER, and AGUARDAR."""
    assert Recommendation("COMPRAR") == Recommendation.COMPRAR
    assert Recommendation("VENDER") == Recommendation.VENDER
    assert Recommendation("AGUARDAR") == Recommendation.AGUARDAR
    with pytest.raises(ValueError):
        Recommendation("MANTER")


def test_recommendation_output_rejects_confidence_out_of_range():
    """Validates that RecommendationOutput rejects confidence outside the 0-1 range."""
    with pytest.raises(ValidationError):
        RecommendationOutput(**{**VALID_FIELDS, "confidence": 1.5})


def test_recommendation_output_rejects_invalid_date_format():
    """Validates that RecommendationOutput rejects date outside the YYYY-MM-DD format."""
    with pytest.raises(ValidationError):
        RecommendationOutput(**{**VALID_FIELDS, "date": "20/06/2026"})


def test_recommendation_output_accepts_valid_data():
    """Validates that valid data is accepted without error."""
    output = RecommendationOutput(**VALID_FIELDS)
    assert output.recommendation == Recommendation.COMPRAR


def test_recommendation_output_serializes_enum_as_plain_string():
    """Validates that model_dump(mode="json") serializes the enum as a plain string.

    Protects against regression of the bug where plain model_dump() returns the
    enum member (<Recommendation.COMPRAR: 'COMPRAR'>) instead of the string
    "COMPRAR", which corrupts CSV writing via csv.DictWriter.
    """
    output = RecommendationOutput(
        ticker="PETR4",
        date="2026-06-19",
        recommendation=Recommendation.COMPRAR,
        confidence=0.75,
        rsi=28.0,
        macd_signal="bullish",
        sentiment_score=0.7,
        sentiment_label="POSITIVO",
        top_headlines=["Manchete exemplo"],
        reasoning="Teste de serialização",
    )

    serialized = output.model_dump(mode="json")

    assert isinstance(serialized["recommendation"], str), (
        f"Esperado str, obtido {type(serialized['recommendation'])}"
    )
    assert serialized["recommendation"] == "COMPRAR", (
        f"Esperado 'COMPRAR', obtido {serialized['recommendation']!r}"
    )
