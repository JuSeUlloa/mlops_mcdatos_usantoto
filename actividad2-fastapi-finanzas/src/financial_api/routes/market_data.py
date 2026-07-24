from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..data import get_market_data

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("/{ticker}/{period}")
def market_data(ticker: str, period: str) -> dict:
    try:
        return get_market_data(ticker, period)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")
