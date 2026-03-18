import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Globale Konfiguration ---
SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", "EUR/RUB": "EURRUB=X", 
    "DAX": "^GDAXI", "EuroStoxx": "^STOXX50E", 
    "Nifty": "^NSEI", "BIST100": "XU100.IS"
}

# Beispiel-Aktien für den Deep-Dive
STOCKS_BY_INDEX = {
    "DAX": ["SAP.DE", "SIE.DE", "AIR.DE"],
    "NASDAQ": ["AAPL", "TSLA", "NVDA"],
    "BIST100": ["THYAO.IS", "ASELS.IS"]
}

def get_data(ticker, interval="4h", period="60d"):
    return yf.download(ticker, period=period, interval=interval)

def monte_carlo_sim(data, days=10, iterations=1000):
    returns = data['Close'].pct_change().dropna()
    last_price = data['Close'].iloc[-1]
    
    # Simulation
    sim_results = np.zeros((days, iterations))
    for i in range(iterations):
        daily_vol = returns.std()
        sim_path = [last_price]
        for _ in range(days - 1):
            sim_path.append(sim_path[-1] * (1 + np.random.normal(0, daily_vol)))
        sim_results[:, i] = sim_path
    return sim_results

# --- Streamlit UI ---
st.title("📈 Pro Trading Dashboard: H4 Momentum & Monte Carlo")

# SCHRITT 1: Allgemeiner Marktüberblick
st.header("1. Markt-Framework (Allgemein)")
cols = st.columns(len(SYMBOLS_GENERAL))
for i, (name, ticker) in enumerate(SYMBOLS_GENERAL.items()):
    df = get_data(ticker, interval="1d", period="1mo")
    change = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
    cols[i].metric(name, f"{df['Close'].iloc[-1]:.2f}", f"{change:.2f}%")

# SCHRITT 2: Deep Dive Einzelaktien
st.header("2. Aktien-Analyse (H4 Momentum)")
selected_index = st.selectbox("Wähle einen Index für Aktien-Details:", list(STOCKS_BY_INDEX.keys()))
selected_stock = st.selectbox("Wähle eine Aktie:", STOCKS_BY_INDEX[selected_index])

if selected_stock:
    data = get_data(selected_stock)
    
    # Momentum H4 (z.B. 14 Perioden)
    data['Momentum'] = data['Close'] - data['Close'].shift(14)
    
    st.subheader(f"Analyse für {selected_stock}")
    st.line_chart(data['Momentum'])

    # Monte Carlo Ausarbeitung
    st.subheader("Monte Carlo Simulation (10 Tage Outlook)")
    sims = monte_carlo_sim(data)
    
    fig, ax = plt.subplots()
    ax.plot(sims, color='gray', alpha=0.1)
    ax.plot(np.mean(sims, axis=1), color='red', label='Erwarteter Pfad')
    st.pyplot(fig)
