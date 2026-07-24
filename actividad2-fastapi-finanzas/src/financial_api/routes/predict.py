from __future__ import annotations

from functools import wraps

from fastapi import APIRouter, HTTPException

from ..entities.prediction import PredictionRequest
from ..predict import (
    get_model_info,
    predict_direction,
    predict_return,
    predict_volatility,
)

router = APIRouter(prefix="/predict", tags=["predict"])


def handle_prediction_errors(func):
    """Decorator para manejar errores de predicción de forma consistente."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al generar predicción: {str(e)}")
    return wrapper


@router.post("/direction")
@handle_prediction_errors
def predict_direction_endpoint(request: PredictionRequest) -> dict:
    """
    Predice la dirección del precio (up/down) usando el modelo de clasificación.
    La probabilidad se calcula REALMENTE usando predict_proba() del modelo.
    """
    symbol = request.symbol.strip().upper()
    prediction = predict_direction(
        ticker=symbol,
        use_cached_data=request.use_cached_data
    )
    
    return {
        "symbol": prediction["symbol"],
        "prediction": prediction["prediction"],
        "probability_up": prediction["probability_up"],
        "model_version": prediction["model_version"],
        "prediction_horizon": prediction["prediction_horizon"],
        "current_close": prediction["current_close"],
    }


@router.post("/return")
@handle_prediction_errors
def predict_return_endpoint(request: PredictionRequest) -> dict:
    """
    Predice el retorno porcentual del próximo día usando el modelo de regresión.
    """
    symbol = request.symbol.strip().upper()
    prediction = predict_return(
        ticker=symbol,
        use_cached_data=request.use_cached_data
    )
    
    return {
        "symbol": prediction["symbol"],
        "predicted_return": prediction["predicted_return"],
        "predicted_return_pct": prediction["predicted_return_pct"],
        "predicted_close": prediction["predicted_close"],
        "current_close": prediction["current_close"],
        "model_version": prediction["model_version"],
        "prediction_horizon": prediction["prediction_horizon"],
    }


@router.post("/volatility")
@handle_prediction_errors
def predict_volatility_endpoint(request: PredictionRequest) -> dict:
    """
    Predice la volatilidad del próximo día usando el modelo de regresión.
    """
    symbol = request.symbol.strip().upper()
    prediction = predict_volatility(
        ticker=symbol,
        use_cached_data=request.use_cached_data
    )
    
    return {
        "symbol": prediction["symbol"],
        "predicted_volatility": prediction["predicted_volatility"],
        "predicted_volatility_pct": prediction["predicted_volatility_pct"],
        "model_version": prediction["model_version"],
        "prediction_horizon": prediction["prediction_horizon"],
    }


@router.get("/model/{ticker}/{model_type}")
def model_info(ticker: str, model_type: str) -> dict:
    """
    Obtiene información de un modelo entrenado.
    
    Args:
        ticker: Símbolo del ticker
        model_type: "classification", "regression_return", "regression_volatility"
    """
    symbol = ticker.strip().upper()
    
    if model_type not in ["classification", "regression_return", "regression_volatility"]:
        raise HTTPException(
            status_code=400,
            detail="model_type debe ser: classification, regression_return, o regression_volatility"
        )
    
    return get_model_info(symbol, model_type)
