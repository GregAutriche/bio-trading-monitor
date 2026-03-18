import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. VERSIONSNUMMERN (Sidebar) ---
st.sidebar.title("System-Info")
st.sidebar.write(f"Streamlit: {st.__version__}")
st.sidebar.write(f"Yfinance: {yf.__version__}")
st.sidebar.write(f"Pandas: {pd.__version__}")

# --- 2. FUNKTIONEN (Ganz oben, mit Cache gegen Hängenbleiben) ---

@st.cache_data(ttl=600) # Speichert Daten für 10 Min, beschleunigt das Laden extrem
def get_market_data(ticker, interval="1d", period="5d"):
    try:
        # Laden mit kurzem Timeout, um Hängenbleiben zu verhindern
        data = yf.download(ticker, period=period, interval=interval, progress=False, timeout=10)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return pd.DataFrame()

# --- 3. KONFIGURATION ---
st.set_page_config(page_title="Trading Monitor", layout="centered")

SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", 
    "EUR/RUB": "EURRUB=X", 
    "DAX Index": "^GDAXI", 
    "EuroStoxx 50": "^STOXX50E", 
    "Nifty 50": "^NSEI", 
    "BIST 100": "XU100.IS"
}

# --- 4. ANZEIGE MARKT-FRAMEWORK ---
st.header("1. Globales Markt-Framework")

for name, ticker in SYMBOLS_GENERAL.items():
    df_gen = get_market_data(ticker)
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        
        # NACHKOMMASTELLEN: Währungen 5, sonst 2
        val_str = f"{last_c:.5f}" if "/" in name else f"{last_c:.2f}"

        st.write(f"**{name}**")
        st.write(f"Kurs: {val_str} | Änderung: {change:+.2f}%")
        st.divider()
    else:
        st.write(f"**{name}**")
        st.write("Warte auf Datenverbindung...")
        st.divider()

# --- 5. TOP 7 AKTIEN AUSWAHL ---
st.header("2. Aktien-Analyse (Top 7)")

STOCKS = {
    "DAX": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "BMW.DE", "MBG.DE"],
    "NASDAQ": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA"],
    "EuroStoxx": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "LIN.DE", "TTE.PA", "SAN.MC"],
    "BIST100": ["THYAO.IS", "ASELS.IS", "KCHOL.IS", "EREGL.IS", "TUPRS.IS", "SISE.IS", "AKBNK.IS"],
    "Nifty": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "HINDUNILVR.NS", "SBIN.NS"]
}

idx_sel = st.selectbox("Index wählen:", list(STOCKS.keys()))
stock_sel = st.selectbox("Aktie wählen:", STOCKS[idx_sel])

# Hier kann nun deine Momentum-Logik folgen...
