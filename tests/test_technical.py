"""Tests for technical indicator functions."""

import pytest
from quantumfinance.data.market_data import fetch_ohlcv
from quantumfinance.features.technical import calculate_indicators
from quantumfinance.universe import TICKERS


@pytest.fixture(scope="module")
def petr4_data():
    """Fetches real PETR4 data once for all tests in the module."""
    return fetch_ohlcv("PETR4")


def test_fetch_ohlcv_returns_dataframe(petr4_data):
    """Validates that fetch_ohlcv returns a non-empty DataFrame with OHLCV columns."""
    assert not petr4_data.empty
    assert "Close" in petr4_data.columns
    assert "Volume" in petr4_data.columns


def test_rsi_in_valid_range(petr4_data):
    """Validates that the calculated RSI is between 0 and 100."""
    features = calculate_indicators(petr4_data)
    assert 0 <= features["rsi"] <= 100


def test_macd_has_expected_fields(petr4_data):
    """Validates that MACD returns the 3 expected components."""
    features = calculate_indicators(petr4_data)
    assert "macd" in features
    assert "macd_signal_line" in features
    assert features["macd_signal"] in ("bullish", "bearish")


def test_market_features_has_required_keys(petr4_data):
    """Validates that the output dictionary contains all required keys."""
    features = calculate_indicators(petr4_data)
    required_keys = {"close", "volume", "rsi", "macd", "sma_20", "sma_50"}
    assert required_keys.issubset(features.keys())


def test_fetch_ohlcv_invalid_ticker_raises():
    """Validates that an invalid ticker raises a handled exception."""
    with pytest.raises(RuntimeError):
        fetch_ohlcv("TICKER_INEXISTENTE_XYZ")


def test_market_features_returns_dict_for_all_tickers():
    """Validates that get_market_features returns a dict for all tickers."""
    from quantumfinance.tools.market_tools import get_market_features
    for ticker in TICKERS:
        result = get_market_features.invoke({"ticker": ticker})
        assert isinstance(result, dict), f"Falhou para {ticker}"
        assert "rsi" in result, f"RSI ausente para {ticker}"
        assert "close" in result, f"Preço ausente para {ticker}"
