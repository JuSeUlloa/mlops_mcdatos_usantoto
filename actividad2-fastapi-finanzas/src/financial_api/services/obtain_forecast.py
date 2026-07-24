from __future__ import annotations

import numpy as np
import pandas as pd
import yfinance as yf


def get_one_year_history(ticker: str) -> pd.DataFrame:
    symbol = ticker.strip().upper()
    data = yf.Ticker(symbol).history(period="1y")

    if data.empty:
        raise ValueError(f"No historical data found for ticker '{symbol}'.")

    return data


def model_forecast(df: pd.DataFrame) -> pd.DataFrame:
    media = df['Close'].mean()
    desviacion = df['Close'].std()

    resultados = np.random.normal(loc=media, scale=desviacion, size=7)

    data_resultados = pd.DataFrame()
    data_resultados['Close_Forecast'] = resultados
    return data_resultados
