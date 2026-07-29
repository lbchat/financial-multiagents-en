"""Runs the backtest with historical sentiment via GDELT/BigQuery (Stage 6.5, Task 5).

90 full days, aligned with the base backtest (Stage 6): BigQuery does not have
the informal rate limit of GDELT's API REST, so there is no longer a need
to reduce the sample size.
"""

from datetime import date, timedelta

from quantumfinance.backtesting.strategy import run_backtest
from quantumfinance.universe import TICKERS

end = date.today().strftime("%Y-%m-%d")
start = (date.today() - timedelta(days=90)).strftime("%Y-%m-%d")

df = run_backtest(
    tickers=TICKERS,
    start_date=start,
    end_date=end,
    output_path="data/backtest_results_gdelt.csv",
    use_gdelt=True,
)
print(f"Backtest concluido: {len(df)} registros")
print(df[["date", "ticker", "recommendation", "sentiment_score", "sentiment_source"]].head(20))
