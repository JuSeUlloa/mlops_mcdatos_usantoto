from __future__ import annotations

import pandas as pd


DEFAULT_LAG_DAYS = [1, 3, 5, 7]


def create_features(df: pd.DataFrame, lag_days: list[int] | None = None) -> pd.DataFrame:
    """
    Crea features para predicción financiera.
    
    IMPORTANTE: Las features solo usan datos disponibles ANTES del día t.
    Los targets (Close_t+1, Return_t+1, etc.) se crean con shift(-1).
    """
    if lag_days is None:
        lag_days = DEFAULT_LAG_DAYS

    df = df.copy()

    columns_to_drop = ["Dividends", "Stock Splits", "Capital Gains"]
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    df["MA_7"] = df["Close"].rolling(window=7).mean()
    df["MA_30"] = df["Close"].rolling(window=30).mean()

    df["Volatility_7"] = df["Close"].rolling(window=7).std()

    df["Return_1d"] = df["Close"].pct_change(1)
    df["Return_7d"] = df["Close"].pct_change(7)

    for lag in lag_days:
        df[f"Lag_{lag}"] = df["Close"].shift(lag)

    df = df.dropna()

    return df


def create_targets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea los targets para los 3 tipos de modelos.
    
    Todos los targets usan datos del DÍA SIGUIENTE (t+1).
    """
    df = df.copy()
    
    df["Target_Return_t1"] = df["Close"].pct_change(1).shift(-1)
    df["Target_Direction_t1"] = (df["Target_Return_t1"] > 0).astype(int)
    df["Target_Volatility_t1"] = df["Close"].pct_change(1).rolling(window=7).std().shift(-1)
    
    return df


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """
    Retorna solo las features disponibles ANTES de la predicción.
    Excluye: Close (target), Open, High, Low (no conocidos antes de predecir)
    """
    exclude = [
        "Close", "Open", "High", "Low",
        "Target_Return_t1", "Target_Direction_t1", "Target_Volatility_t1"
    ]
    return [col for col in df.columns if col not in exclude]


def split_train_test(
    df: pd.DataFrame,
    test_size: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split temporal (no aleatorio) para series de tiempo.
    """
    split_idx = int(len(df) * (1 - test_size))
    return df.iloc[:split_idx], df.iloc[split_idx:]
