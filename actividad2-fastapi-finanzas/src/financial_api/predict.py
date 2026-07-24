from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

from .data import load_processed_data
from .features import create_targets, get_feature_columns


ARTIFACTS_DIR = Path("artifacts")


_model_cache: dict[str, Pipeline] = {}


def load_model(ticker: str, model_type: str = "classification", models_dir: str = "artifacts") -> Pipeline:
    """
    Carga el modelo especificado.
    
    Args:
        ticker: Símbolo del ticker
        model_type: "classification", "regression_return", "regression_volatility"
        models_dir: Directorio de modelos
    """
    symbol = ticker.strip().upper()
    cache_key = f"{symbol}_{model_type}"
    
    if cache_key in _model_cache:
        return _model_cache[cache_key]
    
    model_path = Path(models_dir) / f"{symbol}_{model_type}.joblib"
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo {model_type} para {symbol}. "
            f"Ejecuta: uv run python -m src.financial_api.train --ticker {symbol} --params params.yaml"
        )
    
    model = joblib.load(model_path)
    _model_cache[cache_key] = model
    
    return model


def _prepare_features(
    ticker: str,
    data_dir: str = "data/processed",
    use_cached_data: bool = True
) -> tuple[pd.DataFrame, float]:
    """
    Carga datos, crea targets y retorna features del último día.
    
    Args:
        ticker: Símbolo del ticker
        data_dir: Directorio de datos procesados
        use_cached_data: Si es True, usa datos cacheados
    
    Returns:
        tuple: (features del último día, último precio de cierre)
    """
    symbol = ticker.strip().upper()
    
    df = load_processed_data(symbol, data_dir)
    
    if df is None:
        if use_cached_data:
            raise FileNotFoundError(
                f"No hay datos cacheados para {symbol}. "
                f"Ejecuta GET /market-data/{symbol}/5y primero."
            )
        else:
            raise FileNotFoundError(
                f"No hay datos disponibles para {symbol}. "
                f"Ejecuta GET /market-data/{symbol}/5y para descargar datos."
            )
    
    df = create_targets(df)
    df = df.dropna()
    last_close = float(df["Close"].iloc[-1])
    
    feature_cols = get_feature_columns(df)
    features = df[feature_cols].iloc[-1:]
    
    return features, last_close


def predict_direction(
    ticker: str,
    models_dir: str = "artifacts",
    data_dir: str = "data/processed",
    use_cached_data: bool = True
) -> dict:
    """
    Predice la dirección del precio para el próximo día usando el modelo de clasificación.
    
    La probabilidad se calcula REALMENTE usando predict_proba() del modelo.
    """
    symbol = ticker.strip().upper()
    model = load_model(symbol, "classification", models_dir)
    features, last_close = _prepare_features(symbol, data_dir, use_cached_data)
    
    prediction_class = int(model.predict(features)[0])
    prediction = "up" if prediction_class == 1 else "down"
    probabilities = model.predict_proba(features)[0]
    probability_up = float(probabilities[1])
    
    model_type = type(model.named_steps.get("classifier", model)).__name__
    model_version = f"{model_type.lower()}_v1"
    
    return {
        "symbol": symbol,
        "prediction": prediction,
        "probability_up": round(probability_up, 4),
        "model_version": model_version,
        "prediction_horizon": "next_day",
        "current_close": round(last_close, 2),
    }


def predict_return(
    ticker: str,
    models_dir: str = "artifacts",
    data_dir: str = "data/processed",
    use_cached_data: bool = True
) -> dict:
    """
    Predice el retorno porcentual del próximo día usando el modelo de regresión.
    """
    symbol = ticker.strip().upper()
    model = load_model(symbol, "regression_return", models_dir)
    features, last_close = _prepare_features(symbol, data_dir, use_cached_data)
    
    predicted_return = float(model.predict(features)[0])
    predicted_close = last_close * (1 + predicted_return)
    
    model_type = type(model.named_steps.get("regressor", model)).__name__
    model_version = f"{model_type.lower()}_v1"
    
    return {
        "symbol": symbol,
        "predicted_return": round(predicted_return, 6),
        "predicted_return_pct": round(predicted_return * 100, 4),
        "predicted_close": round(predicted_close, 2),
        "current_close": round(last_close, 2),
        "model_version": model_version,
        "prediction_horizon": "next_day",
    }


def predict_volatility(
    ticker: str,
    models_dir: str = "artifacts",
    data_dir: str = "data/processed",
    use_cached_data: bool = True
) -> dict:
    """
    Predice la volatilidad del próximo día usando el modelo de regresión.
    """
    symbol = ticker.strip().upper()
    model = load_model(symbol, "regression_volatility", models_dir)
    features, _ = _prepare_features(symbol, data_dir, use_cached_data)
    
    predicted_volatility = float(model.predict(features)[0])
    
    model_type = type(model.named_steps.get("regressor", model)).__name__
    model_version = f"{model_type.lower()}_v1"
    
    return {
        "symbol": symbol,
        "predicted_volatility": round(predicted_volatility, 6),
        "predicted_volatility_pct": round(predicted_volatility * 100, 4),
        "model_version": model_version,
        "prediction_horizon": "next_day",
    }


def get_model_info(ticker: str, model_type: str = "classification", models_dir: str = "artifacts") -> dict:
    symbol = ticker.strip().upper()
    model_path = Path(models_dir) / f"{symbol}_{model_type}.joblib"
    
    if not model_path.exists():
        return {
            "exists": False,
            "ticker": symbol,
            "model_type": model_type,
            "message": f"No hay modelo {model_type} entrenado para {symbol}"
        }
    
    model = load_model(symbol, model_type, models_dir)
    
    if model_type == "classification":
        model_name = type(model.named_steps.get("classifier", model)).__name__
    else:
        model_name = type(model.named_steps.get("regressor", model)).__name__
    
    return {
        "exists": True,
        "ticker": symbol,
        "model_type": model_type,
        "model_name": model_name,
        "model_path": str(model_path),
        "file_size_mb": round(model_path.stat().st_size / 1024 / 1024, 2),
        "last_modified": pd.Timestamp.fromtimestamp(model_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    }


def save_model_metadata(ticker: str, metrics: dict, model_path: Path, model_type: str, metadata_path: Path | None = None):
    """
    Guarda metadatos del modelo en un archivo JSON.
    
    Args:
        ticker: Símbolo del ticker
        metrics: Métricas del modelo
        model_path: Path del archivo del modelo
        model_type: Tipo de modelo
        metadata_path: Path opcional para el archivo de metadatos (default: artifacts/model_metadata.json)
    """
    if metadata_path is None:
        metadata_path = ARTIFACTS_DIR / "model_metadata.json"
    
    metadata = {
        "ticker": ticker,
        "model_type": model_type,
        "metrics": metrics,
        "model_path": str(model_path),
        "created_at": pd.Timestamp.now().isoformat()
    }
    
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2))
    
    return metadata
