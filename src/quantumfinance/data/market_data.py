"""Market data collection via yfinance."""

import pandas as pd
import yfinance as yf


def fetch_ohlcv(ticker: str, period: str = "3mo") -> pd.DataFrame:
    """Fetches OHLCV data from Yahoo Finance for the specified ticker."""
    yf_ticker = f"{ticker}.SA"  # Brazilian tickers use the .SA suffix on Yahoo Finance
    try:
        data = yf.download(yf_ticker, period=period, progress=False, auto_adjust=True)
        if data.empty:
            raise ValueError(f"Nenhum dado retornado para {ticker} ({yf_ticker})")
        # yfinance returns MultiIndex columns when downloading 1 ticker in recent versions
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar dados para {ticker}: {e}") from e
