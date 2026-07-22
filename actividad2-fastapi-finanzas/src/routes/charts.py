from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..services.yahoo_services import build_history_chart_png, build_history_chart_png_periods

router = APIRouter(prefix="/charts", tags=["charts"])


@router.get("/history/{ticker}")
def get_history_chart(ticker: str) -> StreamingResponse:
    try:
        image_bytes = build_history_chart_png(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error generating chart.") from exc

    return StreamingResponse(
        content=iter([image_bytes]),
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="{ticker.upper()}_1y.png"'
        },
    )

@router.get("/history/{ticker}/{period}")
def get_history_chart_periods(ticker: str, period: str) -> StreamingResponse:
    try:
        image_bytes = build_history_chart_png_periods(ticker, period)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error generating chart.") from exc

    return StreamingResponse(
        content=iter([image_bytes]),
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="{ticker.upper()}_{period}.png"'
        },
    )