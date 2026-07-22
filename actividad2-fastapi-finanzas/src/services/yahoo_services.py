from __future__ import annotations

import io
import re

import matplotlib 
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


def normalize_period(period: str) -> tuple[str, str]:
    """
    Normaliza el período convirtiendo:
    - Días >= 30 → Meses
    - Meses >= 12 → Años
    
    Retorna: (periodo_normalizado, unidad_original)
    """
    match = re.match(r'^(\d+)(y|mo|d)$', period)
    if not match:
        return period, period[-2:] if period.endswith('mo') else period[-1]
    
    value = int(match.group(1))
    unit = match.group(2)
    
    if unit == 'd' and value >= 30:
        months = value // 30
        return f"{months}mo", 'd'
    elif unit == 'mo' and value >= 12:
        years = value // 12
        return f"{years}y", 'mo'
    
    return period, unit


def get_one_year_history(ticker: str) -> pd.DataFrame:

    symbol = ticker.strip().upper()
    data = yf.Ticker(symbol).history(period="1y")

    if data.empty:
        raise ValueError(f"No historical data found for ticker '{symbol}'.")

    return data

def get_more_years_history(ticker: str, period: str) -> pd.DataFrame:
    symbol = ticker.strip().upper()
    data = yf.Ticker(symbol).history(period=period)
    if data.empty:
        raise ValueError(f"No historical {period} data found for ticker '{symbol}'.")
    return data




def build_history_chart_png(ticker: str) -> bytes:
    df = get_one_year_history(ticker)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df.index, df["Close"], linewidth=2)
    ax.set_title(f"{ticker.upper()} - 1 Year Close Price")
    ax.set_xlabel("Date")
    ax.set_ylabel("Close Price")
    ax.grid(True, alpha=0.3)

    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png", dpi=150)
    plt.close(fig)

    buffer.seek(0)
    return buffer.getvalue()


def build_history_chart_png_periods(ticker: str, period: str) -> bytes:
    normalized_period, original_unit = normalize_period(period)
    
    ejex=''
    if normalized_period.endswith('y'):
        ejex = 'Years'
    elif normalized_period.endswith('mo'):
        ejex = 'Months'
    elif normalized_period.endswith('d'):
        ejex = 'Days'
     
    df = get_more_years_history(ticker, normalized_period)

    fig, ax = plt.subplots(figsize=(10, 5))
    
    if normalized_period.endswith('y'):
        ax.fill_between(df.index, df["Close"], alpha=0.3, color='blue')
        ax.plot(df.index, df["Close"], linewidth=2, color='blue')
        ax.set_title(f"{ticker.upper()} - {ejex} Close Price (Area Chart)")
    elif normalized_period.endswith('mo'):
        ax.plot(df.index, df["Close"], linewidth=2, color='green', marker='o', markersize=4)
        ax.fill_between(df.index, df["Close"], alpha=0.15, color='green')
        ax.set_title(f"{ticker.upper()} - {ejex} Close Price (Line Chart)")
        ax.set_xticks(df.index[::5])
        ax.set_xticklabels([d.strftime('%y-%m-%d') for d in df.index[::5]], rotation=45, ha='right')
    else:
        ax.plot(df.index, df["Close"], linewidth=2, color='red')
        ax.set_title(f"{ticker.upper()} - {ejex} Close Price (Line Chart)")
        ax.set_xticks(df.index[::3])
        ax.set_xticklabels([d.strftime('%y-%m-%d') for d in df.index[::3]], rotation=45, ha='right')
    
    ax.set_xlabel("Date")
    ax.set_ylabel("Close Price")
    ax.grid(True, alpha=0.3)

    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png", dpi=150)
    plt.close(fig)

    buffer.seek(0)
    return buffer.getvalue()