from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from .features import create_features


def download_yahoo_data(ticker: str, period: str) -> pd.DataFrame:
    symbol = ticker.strip().upper()
    df = yf.Ticker(symbol).history(period=period)
    
    if df.empty:
        raise ValueError(f"No se encontraron datos para {symbol} en el periodo de '{period}'")
    return df


def save_raw_data(df: pd.DataFrame, ticker: str, period: str, base_dir: str = "data/raw") -> Path:
    path = Path(base_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    filename = f"{ticker}_{period}.csv"
    filepath = path / filename
    df.to_csv(filepath, index=True)
    
    return filepath


def save_processed_data(df: pd.DataFrame, ticker: str, base_dir: str = "data/processed") -> Path:
    path = Path(base_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    filename = f"{ticker}.csv"
    filepath = path / filename
    df.to_csv(filepath, index=True)
    
    return filepath


def load_raw_data(ticker: str, period: str, base_dir: str = "data/raw") -> pd.DataFrame | None:
    filepath = Path(base_dir) / f"{ticker}_{period}.csv"
    
    if not filepath.exists():
        return None
    
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    return df


def load_processed_data(ticker: str, base_dir: str = "data/processed") -> pd.DataFrame | None:
    filepath = Path(base_dir) / f"{ticker}.csv"
    
    if not filepath.exists():
        return None
    
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    return df


def get_market_data(ticker: str, period: str) -> dict:
    symbol = ticker.strip().upper()
    
    df_raw = None
    data_source = "yahoo_finance"
    
    try:
        df_raw = download_yahoo_data(symbol, period)
        save_raw_data(df_raw, symbol, period)
    except Exception as e:
        df_raw = load_raw_data(symbol, period)
        
        if df_raw is None:
            raise RuntimeError(
                f"No se pudo obtener datos de Yahoo Finance ({str(e)}) y no hay datos cacheados para {symbol}/{period}"
            )
        
        data_source = "local_cache"
    
    df_processed = create_features(df_raw)
    save_processed_data(df_processed, symbol)
    
    features_created = [
        "MA_7", "MA_30", "Volatility_7",
        "Return_1d", "Return_7d",
        "Lag_1", "Lag_3", "Lag_5", "Lag_7"
    ]
    
    return {
        "ticker": symbol,
        "period": period,
        "data_source": data_source,
        "rows": len(df_processed),
        "date_range": {
            "start": df_processed.index.min().strftime("%Y-%m-%d"),
            "end": df_processed.index.max().strftime("%Y-%m-%d")
        },
        "features_created": features_created,
        "files_saved": {
            "raw": f"data/raw/{symbol}_{period}.csv",
            "processed": f"data/processed/{symbol}.csv"
        },
        "message": "Datos descargados y procesados exitosamente" if data_source == "yahoo_finance" else "Usando datos cacheados (Yahoo Finance no disponible)"
    }


def generate_sample_data(
    ticker: str = "AAPL",
    days: int = 1258,
    start_price: float = 150.0,
    volatility: float = 0.02,
    trend: float = 0.0003,
    seed: int = 42
) -> pd.DataFrame:
    np.random.seed(seed)
    
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq="B")
    returns = np.random.normal(trend, volatility, days)
    
    prices = [start_price]
    for r in returns[1:]:
        new_price = prices[-1] * (1 + r)
        prices.append(new_price)
    
    close = np.array(prices)
    high = close * (1 + np.abs(np.random.normal(0, 0.01, days)))
    low = close * (1 - np.abs(np.random.normal(0, 0.01, days)))
    open_prices = close * (1 + np.random.normal(0, 0.005, days))
    volume = np.random.lognormal(mean=17, sigma=0.5, size=days).astype(int)
    
    df = pd.DataFrame({
        "Open": open_prices,
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": volume
    }, index=dates)
    
    df.index.name = "Date"
    
    return df
