"""Tests the agent for all monitored tickers."""
import time

from quantumfinance.agents.orchestrator import ask
from quantumfinance.universe import TICKERS

for ticker in TICKERS:
    print(f"\n{'=' * 50}")
    print(f"TESTANDO: {ticker}")
    print('=' * 50)
    try:
        response = ask(f"Qual a recomendação para {ticker} hoje?")
        print(response)
        print(f"OK: {ticker}")
    except Exception as e:
        print(f"FALHOU: {ticker}: {e}")
    time.sleep(2)  # pause between calls to avoid overloading the API

print("\n\nResumo: verifique data/recommendations.csv")
