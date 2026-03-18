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

# Top 7 Aktien pro Index
STOCKS_BY_INDEX = {
    "DAX": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "BMW.DE", "MBG.DE"],
    "NASDAQ": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA"],
    "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "LIN.DE", "TTE.PA", "SAN.MC"],
    "BIST 100": ["THYAO.IS", "ASELS.IS", "KCHOL.IS", "EREGL.IS", "TUPRS.IS", "SISE.IS", "AKBNK.IS"],
    "Nifty 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "HINDUNILVR.NS", "SBIN.NS"]
}

# --- 3. SEKTION 1: GLOBALER MARKT-FRAMEWORK ---

st.header("1. Globales Markt-Framework")

for name, ticker in SYMBOLS_GENERAL.items():
    df_gen = get_market_data(ticker, interval="1d", period="5d")
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        
        # Währungen 5 Stellen, Indizes 2 Stellen
        is_fx = "/" in name or "X" in ticker
        val_str = f"{last_c:.5f}" if is_fx else f"{last_c:,.2f}"

        st.write(f"**{name}**")
        st.write(f"Kurs: {val_str} | Änderung: {change:+.2f}%")
        st.divider()

# --- 4. SEKTION 2: AKTIEN-ANALYSE (H4 & MONTE CARLO) ---

st.header("2. Aktien-Analyse (Top 7 Auswahl)")

# Auswahl-Menüs untereinander
selected_idx = st.selectbox("Index wählen:", list(STOCKS_BY_INDEX.keys()))
selected_stock = st.selectbox("Aktie wählen:", STOCKS_BY_INDEX[selected_idx])

if selected_stock:
    # H4 Daten für Momentum
    stock_data = get_market_data(selected_stock, interval="4h", period="60d")
    
    if not stock_data.empty and len(stock_data) > 14:
        # Momentum H4 (14 Perioden)
        stock_data['Momentum'] = stock_data['Close'] - stock_data['Close'].shift(14)
        current_p = float(stock_data['Close'].iloc[-1])
        current_m = float(stock_data['Momentum'].iloc[-1])
        
        st.write(f"**Analyse für {selected_stock}**")
        st.write(f"Aktueller Kurs: {current_p:.2f}")
        st.write(f"H4 Momentum (14): {current_m:+.2f}")
        
        # Charts untereinander
        st.line_chart(stock_data['Close'])
        st.caption("Kursverlauf (H4)")
        
        st.area_chart(stock_data['Momentum'])
        st.caption("Momentum Indikator (H4)")

        # --- Monte Carlo Simulation (30 Tage) ---
        st.subheader("Monte Carlo Ausarbeitung (30 Tage Outlook)")
        
        returns = stock_data['Close'].pct_change().dropna()
        daily_vol = returns.std()
        
        plt.figure(figsize=(10, 5))
        sim_ends = []
        
        for _ in range(100): # 100 Pfade für die Visualisierung
            prices = [current_p]
            for _ in range(30):
                prices.append(prices[-1] * (1 + np.random.normal(0, daily_vol)))
            plt.plot(prices, color='gray', alpha=0.1)
            sim_ends.append(prices[-1])
        
        plt.title(f"Simulationspfade für {selected_stock}")
        plt.grid(True, alpha=0.2)
        st.pyplot(plt)
        
        # Statistische Ergebnisse
        avg_target = np.mean(sim_ends)
        st.write(f"Erwarteter Kurs nach 30 Tagen: {avg_target:.2f}")
        st.write(f"Wahrscheinlichkeit für Kursanstieg: {(np.array(sim_ends) > current_p).mean()*100:.1f}%")
        st.divider()
    else:
        st.write("Nicht genügend H4-Daten für diese Aktie verfügbar.")
