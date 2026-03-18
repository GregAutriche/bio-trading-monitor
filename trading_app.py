import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. FUNKTIONEN (Ganz oben zur Vermeidung von NameErrors) ---

@st.cache_data(ttl=600)
def get_market_data(ticker, interval="1d", period="60d"):
    """Lädt Marktdaten sicher von Yahoo Finance mit Cache."""
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False, timeout=15)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return pd.DataFrame()

# --- 2. SEITEN-KONFIGURATION ---

st.set_page_config(page_title="Bio-Trading Monitor", layout="centered")

SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", "EUR/RUB": "EURRUB=X", 
    "DAX Index": "^GDAXI", "EuroStoxx 50": "^STOXX50E", 
    "Nifty 50": "^NSEI", "BIST 100": "XU100.IS"
}

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
        
        # Wetter-Logik für Marktübersicht
        weather = "☀️" if change > 0 else "🌧️"
        
        # NACHKOMMASTELLEN: Währungen 5, Indizes 2
        is_fx = "/" in name or "X" in ticker
        val_str = f"{last_c:.5f}" if is_fx else f"{last_c:,.2f}"

        st.write(f"**{weather} {name}**")
        st.write(f"Kurs: {val_str} | Änderung: {change:+.2f}%")
        st.divider()

# --- 4. SEKTION 2: AKTIEN-ANALYSE (H4 MOMENTUM & MONTE CARLO) ---

st.header("2. Aktien-Analyse (H4 Momentum)")

selected_idx = st.selectbox("Index wählen:", list(STOCKS_BY_INDEX.keys()))
selected_stock = st.selectbox("Aktie wählen:", STOCKS_BY_INDEX[selected_idx])

if selected_stock:
    stock_data = get_market_data(selected_stock, interval="4h", period="60d")
    
    if not stock_data.empty and len(stock_data) > 14:
        # Momentum H4 Berechnung
        stock_data['Momentum'] = stock_data['Close'] - stock_data['Close'].shift(14)
        current_p = float(stock_data['Close'].iloc[-1])
        current_m = float(stock_data['Momentum'].iloc[-1])
        
        # Wetter-Logik basierend auf H4 Momentum
        mom_weather = "☀️ (Bullish)" if current_m > 0 else "🌧️ (Bearish)"
        
        st.write(f"**Analyse für {selected_stock} {mom_weather}**")
        st.write(f"Aktueller Kurs: {current_p:.2f}")
        st.write(f"H4 Momentum (14 Kerzen): {current_m:+.2f}")
        
        st.line_chart(stock_data['Close'])
        st.area_chart(stock_data['Momentum'])

        # --- Monte Carlo Ausarbeitung ---
        st.subheader("Monte Carlo Ausarbeitung (30 Tage Outlook)")
        
        returns = stock_data['Close'].pct_change().dropna()
        daily_vol = returns.std()
        
        plt.figure(figsize=(10, 5))
        sim_ends = []
        for _ in range(100):
            prices = [current_p]
            for _ in range(30):
                prices.append(prices[-1] * (1 + np.random.normal(0, daily_vol)))
            plt.plot(prices, color='gray', alpha=0.1)
            sim_ends.append(prices[-1])
        
        plt.title(f"Simulationspfade für {selected_stock}")
        plt.grid(True, alpha=0.2)
        st.pyplot(plt)
        
        # Statistische Auswertung mit Volatilitäts-Ziel (+5%)
        sim_ends_arr = np.array(sim_ends)
        target_5pct = current_p * 1.05
        prob_5pct = (sim_ends_arr > target_5pct).mean() * 100
        
        st.write(f"Erwarteter Kurs nach 30 Tagen (Mittelwert): {np.mean(sim_ends):.2f}")
        st.write(f"Wahrscheinlichkeit für Kursziel (+5%): {prob_5pct:.1f}%")
        
        # Finale Wetter-Prognose
        final_weather = "☀️" if prob_5pct > 20 else "🌥️" if prob_5pct > 10 else "🌧️"
        st.write(f"**Prognose-Trend: {final_weather}**")
        st.divider()

# Footer / Versionen
st.sidebar.text(f"Streamlit: {st.__version__} | YF: {yf.__version__}")
