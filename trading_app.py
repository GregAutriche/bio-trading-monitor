import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Dashboard")

# --- FUNKTION FÜR LIVE-DATEN ---
def get_market_data():
    # Ticker-Definitionen
    tickers = {
        "EURUSD": "EURUSD=X",
        "EUROSTOXX": "^STOXX50E",  # Euro Stoxx 50 (Standard-Ticker)
        "SP1000": "^GSPC"          # S&P 500 (als verlässlicher Proxy für S&P 1000)
    }
    results = {}
    for key, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            # Daten der letzten 5 Tage für stabilen Delta-Vergleich
            df = ticker.history(period="5d")
            if not df.empty:
                current = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                delta = ((current - prev) / prev) * 100
                results[key] = {"val": current, "delta": delta, "df": df}
        except:
            results[key] = None
    return results

# Daten abrufen
data = get_market_data()

# --- 1. ZEILE: DATUM & UPDATE (YYMMDD) ---
now = datetime.now()
st.write(f"### {now.strftime('%y%m%d')}")
st.write(f"**{now.strftime('%A, %H:%M')} (Letztes Update)**")
st.divider()

# --- 2. ZEILE: EUR/USD ---
st.subheader("Währungs-Fokus")
if data["EURUSD"]:
    val = data["EURUSD"]["val"]
    delta = data["EURUSD"]["delta"]
    col1, col2, col3 = st.columns([1, 1, 1])
    col1.metric("EUR/USD", f"{val:.4f}", f"{delta:.2f}%")
    col2.write("☀️ **Wetter:** Heiter")
    col2.caption("Wetterdaten-Platzhalter")
    col3.write("🔵 **Action:** Monitoring")
st.divider()

# --- 3. ZEILE: INDIZES UNTEREINANDER ---
st.subheader("Markt-Indizes")

# Euro Stoxx Zeile
if data["EUROSTOXX"]:
    col1, col2, col3 = st.columns([1, 1, 1])
    col1.metric("Euro Stoxx 50", f"{data['EUROSTOXX']['val']:.2f}", f"{data['EUROSTOXX']['delta']:.2f}%")
    col2.write("☁️ **Wetter:** Bewölkt")
    col3.write("⚪ **Action:** Wait")

st.write("") # Kleiner Abstand

# S&P 1000 Zeile
if data["SP1000"]:
    col1, col2, col3 = st.columns([1, 1, 1])
    col1.metric("S&P Index", f"{data['SP1000']['val']:.2f}", f"{data['SP1000']['delta']:.2f}%")
    col2.write("☀️ **Wetter:** Sonnig")
    col3.write("🟢 **Action:** Buy")

st.divider()

# --- 4. ZEILE: GRAFIK (Candlestick) ---
st.subheader("Grafik")
if data["SP1000"]:
    df_chart = data["SP1000"]["df"]
    fig = go.Figure(data=[go.Candlestick(
        x=df_chart.index,
        open=df_chart['Open'],
        high=df_chart['High'],
        low=df_chart['Low'],
        close=df_chart['Close'],
        name="Marktverlauf"
    )])
    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=450,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 5. ZEILE: DETAIL INFO ---
st.divider()
st.info("**Detail Info / Beschreibung:**\n\nDas Dashboard zeigt die Korrelation zwischen Wetter-Indikatoren und Marktpreisen. Daten werden live über die Yahoo Finance API bezogen.")
