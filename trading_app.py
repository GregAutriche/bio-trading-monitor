import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. DATEN-FUNKTION (Mit Wetter-Logik für alle) ---
def get_market_data(symbol, is_index=False):
    try:
        t = yf.Ticker(symbol)
        # Intraday-Daten für den 20-Minuten-RSI-Check [cite: 2026-02-07]
        df = t.history(period="5d", interval="15m") 
        if df.empty: df = t.history(period="20d")
        
        preis = df['Close'].iloc[-1]
        # RSI-Berechnung (Position in der Range) [cite: 2026-02-07]
        low14, high14 = df['Close'].tail(14).min(), df['Close'].tail(14).max()
        pos_pct = ((preis - low14) / (high14 - low14)) * 100 if high14 != low14 else 50
        wetter = "☀️" if pos_pct > 90 else "🌧️" if pos_pct < 10 else "☁️"
        
        return preis, wetter, round(pos_pct, 1)
    except: return 0, "❓", 0

# --- 2. HEADER: Wochentag & Datum (Wieder da!) ---
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
st.markdown(f"### 🚀 KONTROLLTURM AKTIV | {tage[jetzt.weekday()]}, {jetzt.strftime('%d.%m.%Y | %H:%M:%S')}")

# --- 3. BASIS-MONITOR (Jetzt mit Wetter) ---
c1, c2, c3 = st.columns(3)
with c1:
    p, w, r = get_market_data("EURUSD=X")
    st.metric(f"EUR/USD {w}", f"{p:.4f}", f"RSI: {r}%")
with c2:
    p, w, r = get_market_data("^GDAXI")
    st.metric(f"DAX (ADR) {w}", f"{p:,.2f}", f"RSI: {r}%")
with c3:
    p, w, r = get_market_data("^IXIC")
    st.metric(f"NASDAQ {w}", f"{p:,.2f}", f"RSI: {r}%")

st.divider()

# --- 4. LEGENDE & CHAMPIONS ---
# (Hier folgt der restliche Code für die 7x7 Champions ohne Index-Ziffern...)
# [Verwende hide_index=True bei st.dataframe() wie in Bild ef0b7295]
