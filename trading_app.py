import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ... [TICKER_DICTS bleibt wie gehabt] ...

def get_trading_advice(curr, sma200, rsi, category):
    """Generiert einfache regelbasierte Empfehlungen."""
    if curr > sma200 and rsi > 50:
        signal = "Kaufen / Halten"
        horizont = "Mittelfristig (bis Trendbruch)" if category != "Währungen" else "Kurzfristig (Intraday/Swing)"
    elif curr < sma200:
        signal = "Warten / Verkaufen"
        horizont = "Cash-Position bevorzugt"
    else:
        signal = "Neutral"
        horizont = "Beobachten"
    return signal, horizont

# UI-Anzeige
signal, horizont = get_trading_advice(curr, sma200, float(df["RSI"].iloc[-1]), cat)

c1, c2, c3 = st.columns(3)
c1.metric("Empfehlung", signal)
c2.metric("Horizont", horizont)
c3.info(f"Basis: {cat}-Analyse")
