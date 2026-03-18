import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. FUNKTIONEN (Muss ganz oben stehen!) ---

def get_market_data(ticker, interval="1d", period="60d"):
    """Lädt Marktdaten sicher von Yahoo Finance."""
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        # Fix für Multi-Index Spalten (yfinance Update)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return pd.DataFrame()

# --- 2. KONFIGURATION ---

st.set_page_config(page_title="Bio-Trading Monitor", layout="centered")

# Markt-Framework Symbole
SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", 
    "EUR/RUB": "EURRUB=X", 
    "DAX Index": "^GDAXI", 
    "EuroStoxx 50": "^STOXX50E", 
    "Nifty 50": "^NSEI", 
    "BIST 100": "XU100.IS"
}

# Top 7 Aktien pro Index
STOCKS_BY_INDEX = {
    "DAX": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "BMW.DE", "MBG.DE"],
    "NASDAQ": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA"],
    "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "LIN.DE", "TTE.PA", "SAN.MC"],
    "BIST 100": ["THYAO.IS", "ASELS.IS", "KCHOL.IS", "EREGL.IS", "TUPRS.IS", "SISE.IS", "AKBNK.IS"],
    "Nifty 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "HINDUNILVR.NS", "SBIN.NS"]
}

# --- 3. SEKTION 1: MARKT-FRAMEWORK ---

st.header("1. Globales Markt-Framework")

for name, ticker in SYMBOLS_GENERAL.items():
    # Aufruf der Funktion (jetzt oben definiert)
    df_gen = get_market_data(ticker, interval="1d", period="5d")
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        
        # LOGIK FÜR NACHKOMMASTELLEN
        if "/" in name:
            # Währungen: 5 Stellen
            val_str = f"{last_c:.5f}"
        else:
            # Indizes (DAX, BIST etc.): 2 Stellen
            val_str = f"{last_c:.2f}"

        st.write(f"**{name}**")
        st.write(f"Kurs: {val_str} | Änderung: {change:+.2f}%")
        st.divider()

# --- 4. SEKTION 2: AKTIEN-ANALYSE ---

st.header("2. Aktien-Analyse (H4 & Monte Carlo)")

idx_choice = st.selectbox("Index wählen:", list(STOCKS_BY_INDEX.keys()))
stock_choice = st.selectbox("Aktie wählen:", STOCKS_BY_INDEX[idx_choice])

if stock_choice:
    stock_data = get_market_data(stock_choice, interval="4h", period="60d")
    
    if not stock_data.empty and len(stock_data) > 14:
        # Momentum H4
        stock_data['Momentum'] = stock_data['Close'] - stock_data['Close'].shift(14)
        
        st.write(f"**{stock_choice}**")
        st.write(f"Kurs: {float(stock_data['Close'].iloc[-1]):.2f}")
        st.write(f"H4 Momentum: {float(stock_data['Momentum'].iloc[-1]):+.2f}")
        
        st.line_chart(stock_data['Close'])
        st.area_chart(stock_data['Momentum'])

        # Monte Carlo Simulation
        st.subheader("Monte Carlo (30 Tage)")
        returns = stock_data['Close'].pct_change().dropna()
        last_p = float(stock_data['Close'].iloc[-1])
        
        plt.figure(figsize=(10, 5))
        for _ in range(100):
            prices = [last_p]
            for _ in range(30):
                prices.append(prices[-1] * (1 + np.random.normal(0, returns.std())))
            plt.plot(prices, color='gray', alpha=0.1)
        plt.title(f"Simulation {stock_choice}")
        st.pyplot(plt)
