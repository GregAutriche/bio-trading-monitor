import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Konfiguration ---
st.set_page_config(page_title="Bio-Trading Monitor", layout="centered")

SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", 
    "EUR/RUB": "EURRUB=X", 
    "DAX": "^GDAXI", 
    "EuroStoxx": "^STOXX50E", 
    "Nifty": "^NSEI", 
    "BIST100": "XU100.IS"
}

# --- MARKTÜBERBLICK UNTEREINANDER ---
st.title("Marktüberblick")

for name, ticker in SYMBOLS_GENERAL.items():
    df_gen = yf.download(ticker, period="5d", interval="1d", progress=False)
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        
        # Formatierung: Währungen 5 Stellen, Indizes 2 Stellen
        is_fx = "/" in name or "X" in ticker
        val_str = f"{last_c:.5f}" if is_fx else f"{last_c:,.2f}"

        # Schlichte Anzeige ohne Icons/Infoboxen
        st.write(f"**{name}**")
        st.write(f"Kurs: {val_str} | Änderung: {change:+.2f}%")
        st.divider()

# --- H4 MOMENTUM & MONTE CARLO ---
st.header("H4 Momentum Analyse")

# Beispiel-Aktie (kannst du durch Selectbox ersetzen)
selected_stock = "SAP.DE" 
stock_data = yf.download(selected_stock, period="60d", interval="4h", progress=False)

if not stock_data.empty:
    # Momentum Berechnung
    stock_data['Momentum'] = stock_data['Close'] - stock_data['Close'].shift(14)
    
    st.subheader(f"Kursverlauf: {selected_stock}")
    st.line_chart(stock_data['Close'])
    
    st.subheader("Momentum (H4)")
    st.area_chart(stock_data['Momentum'])

    # Monte Carlo Simulation
    st.subheader("Monte Carlo Ausarbeitung (30 Tage)")
    returns = stock_data['Close'].pct_change().dropna()
    last_price = stock_data['Close'].iloc[-1]
    
    # 100 Simulationen für die Übersicht
    plt.figure(figsize=(10, 5))
    for _ in range(100):
        prices = [last_price]
        for _ in range(30):
            prices.append(prices[-1] * (1 + np.random.normal(0, returns.std())))
        plt.plot(prices, color='gray', alpha=0.1)
    
    plt.title(f"Simulationspfade {selected_stock}")
    plt.grid(True, alpha=0.3)
    st.pyplot(plt)
