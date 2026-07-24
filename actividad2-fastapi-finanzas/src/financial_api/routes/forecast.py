from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..services.obtain_forecast import model_forecast, get_one_year_history

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/forecast/{ticker}")
def get_forecast_7d(ticker: str) -> dict[str, object]:
    symbol = ticker.strip().upper()

    try:
        dataset = get_one_year_history(symbol)
        pronostico = model_forecast(dataset)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error generando la prediccion!") from exc

    forecast = [
        {"day": day, "close_forecast": float(value)}
        for day, value in enumerate(pronostico["Close_Forecast"].tolist(), start=1)
    ]
    return {"ticker": symbol, "forecast": forecast}
