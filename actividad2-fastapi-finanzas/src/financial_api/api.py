from __future__ import annotations

from fastapi import FastAPI

from .routes.charts import router as charts_router
from .routes.forecast import router as forecast_router
from .routes.market_data import router as market_data_router
from .routes.predict import router as predict_router


app = FastAPI(
    title="SmartPortfolio API",
    description="API for market charts, portfolio analytics, and ML predictions",
    version="0.2.0",
)

app.include_router(charts_router)
app.include_router(forecast_router)
app.include_router(market_data_router)
app.include_router(predict_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "SmartPortfolio API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
