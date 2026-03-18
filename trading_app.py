import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. FUNKTIONEN DEFINIEREN ---

def get_market_data(ticker, interval="1d", period="60d"):
    """Lädt Marktdaten von Yahoo Finance."""
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        # Multi-Index-Spalten von yfinance bereinigen, falls vorhanden
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return pd.DataFrame()

# --- 2. KONFIGURATION ---

st.set_page_config(page_title="Bio-Trading Monitor", layout="centered")

# Märkte für Sektion 1
SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", "EUR/RUB": "EURRUB=X", 
    "DAX Index": "^GDAXI", "EuroStoxx 50": "^STOXX50E", 
    "Nifty 50": "^NSEI", "BIST 100": "XU100.IS"
}

# Aktien für Sektion 2
STOCKS_BY_INDEX = {
    "DAX": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "BMW.DE"],
    "NASDAQ": ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META"]
}

# --- 3. SEKTION 1: GLOBALER MARKT-FRAMEWORK ---

st.header("1. Globales Markt-Framework")

for name, ticker in SYMBOLS_GENERAL.items():
    df_gen = get_market_data(ticker, interval="1d", period="5d")
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        
        is_fx = "/" in name or "X" in ticker
        val_str = f"{last_c:.5f}" if is_fx else f"{last_c:,.2f}"

        st.write(f"**{name}**")
        st.write(f"Kurs: {val_str} | Änderung: {change:+.2f}%")
        st.divider()

# --- 4. SEKTION 2: EINZELAKTIEN ANALYSE (H4 & MONTE CARLO) ---

st.header("2. Aktien-Analyse (H4 Momentum)")

# Auswahl-Menüs
selected_idx = st.selectbox("Index wählen:", list(STOCKS_BY_INDEX.keys()))
selected_stock = st.selectbox("Aktie wählen:", STOCKS_BY_INDEX[selected_idx])

if selected_stock:
    # H4 Daten für Momentum (14 Perioden)
    stock_data = get_market_data(selected_stock, interval="4h", period="60d")
    
    if not stock_data.empty and len(stock_data) > 14:
        # Momentum H4 Berechnung
        stock_data['Momentum'] = stock_data['Close'] - stock_data['Close'].shift(14)
        current_close = float(stock_data['Close'].iloc[-1])
        current_mom = float(stock_data['Momentum'].iloc[-1])

        st.write(f"**Analyse für {selected_stock}**")
        st.write(f"Aktueller Kurs: {current_close:.2f}")
        st.write(f"H4 Momentum (14): {current_mom:+.2f}")
        
        # Charts untereinander
        st.line_chart(stock_data['Close'], use_container_width=True)
        st.caption("Kursverlauf (H4)")
        
        st.area_chart(stock_data['Momentum'], use_container_width=True)
        st.caption("Momentum Indikator (H4)")

        # --- Monte Carlo Ausarbeitung ---
        st.subheader("Monte Carlo Simulation (30 Tage)")
        
        returns = stock_data['Close'].pct_change().dropna()
        daily_vol = returns.std()
        
        # Simulation von 100 Pfaden
        plt.figure(figsize=(10, 5))
        simulated_end_prices = []
        
        for _ in range(100):
            prices = [current_close]
            for _ in range(30):
                prices.append(prices[-1] * (1 + np.random.normal(0, daily_vol)))
            plt.plot(prices, color='gray', alpha=0.1)
            simulated_end_prices.append(prices[-1])
        
        # Mittelwert-Pfad hervorheben
        avg_end_price = np.mean(simulated_end_prices)
        plt.title(f"Simulationspfade für {selected_stock}")
        plt.grid(True, alpha=0.2)
        st.pyplot(plt)
        
        # Statistische Auswertung unter der Grafik
        st.write(f"Erwarteter Kurs nach 30 Tagen (Mittelwert): {avg_end_price:.2f}")
        st.write(f"Wahrscheinlichkeit für Kurssteigerung: {(np.array(simulated_end_prices) > current_close).mean()*100:.1f}%")
        st.divider()
    else:
        st.write("Nicht genügend H4-Daten für diese Aktie verfügbar.")
