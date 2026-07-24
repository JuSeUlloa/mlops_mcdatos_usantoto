from __future__ import annotations

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    symbol: str
    prediction_horizon: int 
    use_cached_data: bool 
