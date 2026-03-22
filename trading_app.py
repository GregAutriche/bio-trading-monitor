import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. VOLLSTÄNDIGE TICKER-LISTEN (STAND MÄRZ 2026) ---
# DAX 40 (Vollständig)
DAX_40_TICKERS = [
    "ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "BNR.DE",
    "CBK.DE", "CON.DE", "1COV.DE", "DTG.DE", "DBK.DE", "DB1.DE", "DHL.DE", "DTE.DE",
    "EOAN.DE", "FRE.DE", "FME.DE", "MTX.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE",
    "MRK.DE", "MUV2.DE", "PAH3.DE", "PUM.DE", "QIA.DE", "RHM.DE", "RWE.DE", "SAP.DE",
    "SRT3.DE", "SIE.DE", "ENR.DE", "SHL.DE", "SY1.DE", "TKA.DE", "VOW3.DE", "VNA.DE"
]

# NASDAQ 100 (Auszug der Top-Werte & Neuaufnahmen wie Palantir/Microstrategy)
NASDAQ_100_TICKERS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "PEP",
    "COST", "ADBE", "CSCO", "NFLX", "AMD", "TMUS", "CMCSA", "INTU", "INTC", "AMAT",
    "PLTR", "MSTR", "QCOM", "TXN", "HON", "ISRG", "BKNG", "VRTX", "PANW", "MU"
]

TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", 
    "^GDAXI": "DAX 40 Index", "^NDX": "NASDAQ 100 Index",
    "^STOXX50E": "EuroStoxx 50", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50"
}

WEATHER_STRUCTURE = [
    ["EURUSD=X", "EURRUB=X"],
    ["^GDAXI", "^NDX"],
    ["^STOXX50E", "XU100.IS", "^NSEI"]
]

# --- 3. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="5d", interval="1h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def extract_val(df, column, idx):
    try:
        val = df[column].iloc[idx]
        return float(val.iloc) if hasattr(val, 'iloc') else float(val)
    except: return 0.0

# --- 4. TOP 5 CALL/PUT LOGIK ---
def get_top_5_signals(tickers):
    signals = []
    for t in tickers:
        df = get_data(t, period="5d", interval="1h")
        if not df.empty:
            cp = extract_val(df, 'Close', -1)
            ret = ((cp / extract_val(df, 'Close', -2)) - 1) * 100
            signals.append({'Ticker': t, 'Preis': cp, 'Change': ret})
    
    df_sig = pd.DataFrame(signals)
    top_calls = df_sig.sort_values(by='Change', ascending=False).head(5)
    top_puts = df_sig.sort_values(by='Change', ascending=True).head(5)
    return top_calls, top_puts

# --- 5. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# MARKT-WETTER
st.subheader("🌐 Globales Markt-Wetter")
for row in WEATHER_STRUCTURE:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        w_data = get_data(t)
        if not w_data.empty:
            cp_w = extract_val(w_data, 'Close', -1)
            chg_w = ((cp_w / extract_val(w_data, 'Close', -2)) - 1) * 100
            prec = 5 if "=X" in t else 2
            color = "#00FFA3" if chg_w > 0.15 else "#FF4B4B" if chg_w < -0.15 else "#FFD700"
            with cols[i]:
                st.markdown(f'<div style="border:1px solid {color}; padding:10px; border-radius:10px; text-align:center;">'
                            f'<b>{TICKER_NAMES.get(t, t)}</b><br><span style="font-size:1.2rem;">{cp_w:,.{prec}f}</span>'
                            f'<br><span style="color:{color};">{chg_w:+.2f}%</span></div>', unsafe_allow_html=True)

st.divider()

# TOP 5 TABELLEN
st.subheader("📊 Top 5 Handels-Signale (DAX & NASDAQ)")
t_col1, t_col2 = st.columns(2)

with st.spinner("Berechne Top-Signale..."):
    all_tickers = DAX_40_TICKERS + NASDAQ_100_TICKERS
    calls, puts = get_top_5_signals(all_tickers)

with t_col1:
    st.markdown("### 🟢 Top 5 CALL (Bullish)")
    st.table(calls[['Ticker', 'Preis', 'Change']].style.format({'Preis': '{:.2f}', 'Change': '{:+.2f}%'}))

with t_col2:
    st.markdown("### 🔴 Top 5 PUT (Bearish)")
    st.table(puts[['Ticker', 'Ticker', 'Preis', 'Change']].style.format({'Preis': '{:.2f}', 'Change': '{:+.2f}%'}))

st.divider()

# AKTIEN-DETAIL (Bisherige Logik)
st.subheader("🔍 Einzelwert-Analyse")
sel_stock = st.selectbox("Aktie wählen:", all_tickers)
# ... [Hier folgt der Rest deiner Analyse-Logik wie oben im Projekt]
