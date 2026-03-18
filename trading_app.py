import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. FUNKTIONEN (Müssen ganz oben stehen) ---

def get_market_data(ticker, interval="1d", period="60d"):
    """Lädt Marktdaten sicher von Yahoo Finance."""
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        # Fix für neuere yfinance Versionen (MultiIndex Spalten entfernen)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return pd.DataFrame()

# --- 2. KONFIGURATION ---

st.set_page_config(page_title="Bio-Trading Monitor", layout="centered")

# Markt-Framework Symbole
SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", "EUR/RUB": "EURRUB=X", 
    "DAX Index": "^GDAXI", "EuroStoxx 50": "^STOXX50E", 
    "Nifty 50": "^NSEI", "BIST 100": "XU100.IS"
}

# Aktien-Auswahl
STOCKS_BY_INDEX = {
    "DAX": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "BMW.DE"],
    "NASDAQ": ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META"],
    "EURO STOXX": ["ASML.AS", "MC.PA", "SAP.DE"],
    "NIFTY": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"],
    "BIST 100": ["THYAO.IS", "ASELS.IS", "KCHOL.IS"]
}

# --- 3. SEKTION 1: GLOBALER MARKT-FRAMEWORK ---

st.header("1. Globales Markt-Framework")

for name, ticker in SYMBOLS_GENERAL.items():
    # Hier wird die oben definierte Funktion aufgerufen
    df_gen = get_market_data(ticker, interval="1d", period="5d")
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        
        # Währungen 5 Stellen, sonst 2 Stellen
        is_fx = "/" in name or "X" in ticker
        val_str = f"{last_c:.5f}" if is_fx else f"{last_c:,.2f}"

        st.write(f"**{name}**")
        st.write(f"Kurs: {val_str} | Änderung: {change:+.2f}%")
        st.divider()

# --- 4. SEKTION 2: AKTIEN-ANALYSE (H4 & MONTE CARLO) ---

st.header("2. Aktien-Analyse (H4 Momentum)")

# Auswahl-Menüs
selected_idx = st.selectbox("Index wählen:", list(STOCKS_BY_INDEX.keys()))
selected_stock = st.selectbox("Aktie wählen:", STOCKS_BY_INDEX[selected_idx])

if selected_stock:
    # H4 Daten für Momentum
    stock_data = get_market_data(selected_stock, interval="4h", period="60d")
    
    if not stock_data.empty and len(stock_data) > 14:
        # Momentum H4 (14 Perioden)
        stock_data['Momentum'] = stock_data['Close'] - stock_data['Close'].shift(14)
        
        st.write(f"**Analyse für {selected_stock}**")
        st.write(f"H4 Momentum (14): {float(stock_data['Momentum'].iloc[-1]):+.2f}")
        
        st.line_chart(stock_data['Close'])
        st.area_chart(stock_data['Momentum'])

        # --- Monte Carlo ---
        st.subheader("Monte Carlo Ausarbeitung (30 Tage)")
        returns = stock_data['Close'].pct_change().dropna()
        last_p = float(stock_data['Close'].iloc[-1])
        
        plt.figure(figsize=(10, 5))
        for _ in range(100):
            prices = [last_p]
            for _ in range(30):
                prices.append(prices[-1] * (1 + np.random.normal(0, returns.std())))
            plt.plot(prices, color='gray', alpha=0.1)
        
        plt.title(f"Simulationspfade {selected_stock}")
        plt.grid(True, alpha=0.2)
        st.pyplot(plt)
