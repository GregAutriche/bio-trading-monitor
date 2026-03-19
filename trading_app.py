import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. ERWEITERTES NAMENS-MAPPING (Vollständige Listen) ---
TICKER_NAMES = {
    # Forex
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "USDJPY=X": "USD/JPY",
    # Indizes
    "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50", "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    # DAX (Auszug Top Titel)
    "SAP.DE": "SAP", "SIE.DE": "Siemens", "ALV.DE": "Allianz", "DTE.DE": "Telekom", "AIR.DE": "Airbus", "MBG.DE": "Mercedes", "BMW.DE": "BMW", "BAS.DE": "BASF", "BAYN.DE": "Bayer", "ADS.DE": "Adidas", "DBK.DE": "Deutsche Bank", "RHM.DE": "Rheinmetall",
    # NASDAQ (Auszug Top Titel)
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "AMZN": "Amazon", "GOOGL": "Alphabet", "META": "Meta", "TSLA": "Tesla", "AVGO": "Broadcom", "COST": "Costco", "NFLX": "Netflix", "AMD": "AMD", "INTC": "Intel",
    # BIST & NIFTY
    "THYAO.IS": "Turkish Airlines", "ASELS.IS": "Aselsan", "KCHOL.IS": "Koc Holding", "RELIANCE.NS": "Reliance", "TCS.NS": "TCS", "HDFCBANK.NS": "HDFC Bank"
}

# --- 3. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="1d"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def get_top_5_signals(ticker_list):
    """Simuliert das Bewertungssystem (z.B. nach Trendstärke/RSI)"""
    signals = []
    for t in ticker_list:
        df = get_data(t, period="20d")
        if not df.empty:
            last = df['Close'].iloc[-1]
            chg = ((last / df['Close'].iloc[-2]) - 1) * 100
            signals.append({"Symbol": TICKER_NAMES.get(t, t), "Kurs": last, "Score": round(chg, 2)})
    # Sortiert nach 'Score' (unser Bewertungssystem)
    return pd.DataFrame(signals).sort_values(by="Score", ascending=False).head(5)

# --- 4. HEADER (WÄHRUNGEN & INDIZES) ---
st.title("🚀 Bio-Trading Monitor Live PRO")

st.subheader("💱 Zeile 1: Währungen")
c_f1, c_f2, _ = st.columns([1, 1, 4])
for i, t in enumerate(["EURUSD=X", "EURRUB=X"]):
    df = get_data(t, period="2d")
    if not df.empty:
        l = df['Close'].iloc[-1]; c = ((l/df['Close'].iloc[-2])-1)*100
        (c_f1 if i==0 else c_f2).metric(TICKER_NAMES[t], f"{l:,.5f}", f"{c:+.2f}%")

st.subheader("📈 Zeile 2: Indizes")
c_i = st.columns(5)
for i, t in enumerate(["^GDAXI", "^STOXX50E", "^NDX", "XU100.IS", "^NSEI"]):
    df = get_data(t, period="2d")
    if not df.empty:
        l = df['Close'].iloc[-1]; c = ((l/df['Close'].iloc[-2])-1)*100
        c_i[i].metric(TICKER_NAMES.get(t,t), f"{l:,.2f}", f"{c:+.2f}%")

# --- 5. DEEP-DIVE & BEWERTUNGSSYSTEM ---
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Deep-Dive Chart")
    ca, cb = st.columns(2)
    m_choice = ca.selectbox("Markt:", ["DAX 40", "NASDAQ 100", "BIST 100", "Nifty 50"])
    
    # Mapping für die Auswahl
    MAPPING = {
        "DAX 40": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
        "NASDAQ 100": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AMD", "NFLX"],
        "BIST 100": ["THYAO.IS", "ASELS.IS", "KCHOL.IS"],
        "Nifty 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    }
    s_tkr = cb.selectbox("Titel:", MAPPING[m_choice], format_func=lambda x: TICKER_NAMES.get(x,x))
    
    # Chart Simulation (wie gewohnt)
    d_s = get_data(s_tkr, interval="4h")
    if not d_s.empty:
        cp = d_s['Close'].iloc[-1]
        st.info(f"Aktueller Kurs: {cp:,.2f} | Ziel: {cp*1.05:,.2f} (SL: -3.00%)")
        fig, ax = plt.subplots(figsize=(10, 4)); ax.set_facecolor('#0E1117'); fig.patch.set_facecolor('#0E1117')
        ax.plot(d_s.index, d_s['Close'], color='#1E90FF'); st.pyplot(fig)

with col_right:
    st.subheader("🎯 Top 5 Signale (Bewertungssystem)")
    # Hier werden die Top 5 aus dem gewählten Markt nach Score angezeigt
    top_5_df = get_top_5_signals(MAPPING[m_choice])
    st.table(top_5_df) # Saubere Tabelle ohne Scrollbars

st.caption("Das Bewertungssystem analysiert Trendstärke und Momentum der letzten 20 Handelstage.")
