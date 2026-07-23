"""Historical features and forward returns for backtesting, without look-ahead bias."""

import pandas as pd
import yfinance as yf

from quantumfinance.features.technical import calculate_indicators

IBOVESPA_TICKER = "^BVSP"


def _is_trading_day(yf_ticker: str, date: str) -> bool:
    """Confirms that `date` corresponds to an actual trading day (not a weekend or holiday).

    `dayofweek` only excludes weekends — B3 holidays (e.g., Carnival) go
    undetected and would make yfinance silently "slide" to the next available
    trading day, duplicating values across consecutive holiday dates.
    """
    target_date = pd.Timestamp(date)
    try:
        probe = yf.download(
            yf_ticker,
            start=date,
            end=(target_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=True,
        )
    except Exception:
        return False

    if probe.empty:
        return False

    return probe.index[0].strftime("%Y-%m-%d") == target_date.strftime("%Y-%m-%d")


def get_historical_features(ticker: str, date: str) -> dict | None:
    """Calculates technical indicators using only data before `date` (without look-ahead bias)."""
    target_date = pd.Timestamp(date)
    if target_date.dayofweek >= 5:
        return None  # weekend, not a business day

    yf_ticker = f"{ticker}.SA"
    if not _is_trading_day(yf_ticker, date):
        return None  # holiday — no trading session on this date

    start_date = target_date - pd.Timedelta(days=90)

    try:
        # end=date is exclusive in yfinance: ensures no data from `date`
        # onward is used to calculate the indicators.
        data = yf.download(
            yf_ticker,
            start=start_date.strftime("%Y-%m-%d"),
            end=date,
            progress=False,
            auto_adjust=True,
        )
    except Exception:
        return None

    if data.empty:
        return None

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return calculate_indicators(data)


def _compute_forward_return(yf_ticker: str, date: str, days: int) -> float | None:
    """Calculates the percentage return between the price on `date` and `days` trading days later."""
    target_date = pd.Timestamp(date)
    end_date = target_date + pd.Timedelta(days=days * 2 + 5)  # buffer for weekends/holidays

    try:
        data = yf.download(
            yf_ticker,
            start=date,
            end=end_date.strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=True,
        )
    except Exception:
        return None

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if data.empty or len(data) <= days:
        return None

    # if `date` was not a trading day (holiday), yfinance "slides" to the next
    # available day — without this check, consecutive holiday dates would yield
    # the same return (same initial price), as if they were the same day.
    if data.index[0].strftime("%Y-%m-%d") != target_date.strftime("%Y-%m-%d"):
        return None

    start_price = float(data["Close"].iloc[0])
    end_price = float(data["Close"].iloc[days])
    return round((end_price - start_price) / start_price * 100, 4)


def get_forward_return(ticker: str, date: str, days: int = 5) -> float | None:
    """Returns the ticker's actual percentage return over the next `days` trading days after `date`."""
    return _compute_forward_return(f"{ticker}.SA", date, days)


def get_ibovespa_return(date: str, days: int = 5) -> float | None:
    """Returns the Ibovespa percentage return over the next `days` trading days after `date`."""
    return _compute_forward_return(IBOVESPA_TICKER, date, days)
