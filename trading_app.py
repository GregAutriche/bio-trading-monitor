import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-LISTEN ---
DAX_40_TICKERS = [
    "ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "BNR.DE",
    "CBK.DE", "CON.DE", "1COV.DE", "DTG.DE", "DBK.DE", "DB1.DE", "DHL.DE", "DTE.DE",
    "EOAN.DE", "FRE.DE", "FME.DE", "MTX.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE",
    "MRK.DE", "MUV2.DE", "PAH3.DE", "PUM.DE", "QIA.DE", "RHM.DE", "RWE.DE", "SAP.DE",
    "SRT3.DE", "SIE.DE", "ENR.DE", "SHL.DE", "SY1.DE", "TKA.DE", "VOW3.DE", "VNA.DE"
]

NASDAQ_100_TICKERS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "PEP", "COST",
    "ADBE", "CSCO", "NFLX", "AMD", "PLTR", "MSTR", "QCOM", "TXN", "ISRG", "PANW"
]

TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", 
    "^GDAXI": "DAX 40", "^NDX": "NASDAQ 100",
    "^STOXX50E": "EuroStoxx 50", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50"
}

WEATHER_STRUCTURE = [["EURUSD=X", "EURRUB=X"], ["^GDAXI", "^NDX"], ["^STOXX50E", "XU100.IS", "^NSEI"]]

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
        return float(val.iloc[0]) if hasattr(val, 'iloc') else float(val)
    except: return 0.0

def get_top_5_signals(tickers):
    signals = []
    for t in tickers:
        df = get_data(t)
        if not df.empty and len(df) > 1:
            cp = extract_val(df, 'Close', -1)
            prev = extract_val(df, 'Close', -2)
            ret = ((cp / prev) - 1) * 100 if prev > 0 else 0
            signals.append({'Ticker': t, 'Preis': cp, 'Change': ret})
    
    df_sig = pd.DataFrame(signals)
    if df_sig.empty: return pd.DataFrame(), pd.DataFrame()
    return df_sig.nlargest(5, 'Change'), df_sig.nsmallest(5, 'Change')

# --- 4. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# MARKT-WETTER (3 Zeilen)
st.subheader("🌐 Globales Markt-Wetter")
for row in WEATHER_STRUCTURE:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        w_data = get_data(t)
        if not w_data.empty:
            cp_w = extract_val(w_data, 'Close', -1)
            chg_w = ((cp_w / extract_val(w_data, 'Close', -2)) - 1) * 100
            prec = 5 if "=X" in t else 2
            color = "#00FFA3" if chg_w > 0.1 else "#FF4B4B" if chg_w < -0.1 else "#FFD700"
            with cols[i]:
                st.markdown(f'<div style="border:1px solid {color}; padding:10px; border-radius:10px; text-align:center; background:rgba(255,255,255,0.02);">'
                            f'<small>{TICKER_NAMES.get(t, t)}</small><br><b style="font-size:1.2rem;">{cp_w:,.{prec}f}</b>'
                            f'<br><span style="color:{color}; font-size:0.9rem;">{chg_w:+.2f}%</span></div>', unsafe_allow_html=True)

st.divider()

# TOP 5 TABELLEN (FEHLER BEHOBEN & FARBEN KORRIGIERT)
st.subheader("📊 Top 5 Handels-Signale (DAX & NASDAQ)")
t_col1, t_col2 = st.columns(2)

with st.spinner("Scanne Märkte..."):
    calls, puts = get_top_5_signals(DAX_40_TICKERS + NASDAQ_100_TICKERS)

if not calls.empty:
    with t_col1:
        st.markdown("<h3 style='color:#00FFA3;'>🟢 Top 5 CALL (Stärkste)</h3>", unsafe_allow_html=True)
        # Korrektur: Nur einfache Spaltenliste, kein doppelter Ticker
        st.table(calls[['Ticker', 'Preis', 'Change']].style.format({'Preis': '{:.2f}', 'Change': '{:+.2f}%'})\
                 .set_properties(**{'background-color': 'rgba(0, 255, 163, 0.05)', 'color': '#00FFA3', 'border-color': '#00FFA3'}))

    with t_col2:
        st.markdown("<h3 style='color:#FF4B4B;'>🔴 Top 5 PUT (Schwächste)</h3>", unsafe_allow_html=True)
        # Korrektur: 'Ticker' war doppelt -> jetzt gefixt
        st.table(puts[['Ticker', 'Preis', 'Change']].style.format({'Preis': '{:.2f}', 'Change': '{:+.2f}%'})\
                 .set_properties(**{'background-color': 'rgba(255, 75, 75, 0.05)', 'color': '#FF4B4B', 'border-color': '#FF4B4B'}))

st.divider()

# EINZELWERT ANALYSE
st.subheader("🔍 Analyse Einzelwert")
all_stocks = sorted(DAX_40_TICKERS + NASDAQ_100_TICKERS)
sel_stock = st.selectbox("Aktie wählen:", all_stocks)

d_s = get_data(sel_stock, period="60d", interval="4h")
if not d_s.empty:
    cp = extract_val(d_s, 'Close', -1)
    st.metric(f"Aktueller Kurs: {sel_stock}", f"{cp:,.2f}")
    st.line_chart(d_s['Close'])

st.info(f"🕒 Stand: {pd.Timestamp.now().strftime('%H:%M:%S')} | Quelle: Yahoo Finance")
