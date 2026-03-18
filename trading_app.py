import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Konfiguration ---
st.set_page_config(page_title="Bio-Trading Monitor", layout="wide")

# Symbole für den allgemeinen Marktüberblick
SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", 
    "EUR/RUB": "EURRUB=X", 
    "DAX": "^GDAXI", 
    "EuroStoxx": "^STOXX50E", 
    "Nifty": "^NSEI", 
    "BIST100": "XU100.IS"
}

# Aktien-Auswahl nach Index
STOCKS_BY_INDEX = {
    "DAX": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE"],
    "EuroStoxx": ["ASML.AS", "MC.PA", "SAP.DE"],
    "NASDAQ": ["AAPL", "TSLA", "NVDA", "MSFT"],
    "Nifty": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"],
    "BIST100": ["THYAO.IS", "ASELS.IS", "KCHOL.IS"]
}

# --- Funktionen ---

@st.cache_data(ttl=3600) # Cache für 1 Stunde, um API-Limits zu schonen
def get_market_data(ticker, interval="1d", period="60d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        return data
    except Exception:
        return pd.DataFrame()

def run_monte_carlo(data, days=30, iterations=500):
    """Berechnet 500 mögliche Kurspfade für die nächsten 30 Tage."""
    returns = data['Close'].pct_change().dropna()
    last_price = data['Close'].iloc[-1]
    daily_vol = returns.std()
    
    simulation_df = pd.DataFrame()
    for i in range(iterations):
        prices = [last_price]
        for _ in range(days):
            prices.append(prices[-1] * (1 + np.random.normal(0, daily_vol)))
        simulation_df[i] = prices
    return simulation_df

# --- Streamlit UI ---

st.title("📊 Bio-Trading Monitor: H4 Momentum & Monte Carlo")

# SEKTION 1: Allgemeiner Marktüberblick
st.header("1. Globales Markt-Framework")
cols = st.columns(len(SYMBOLS_GENERAL))

for i, (name, ticker) in enumerate(SYMBOLS_GENERAL.items()):
    df_gen = get_market_data(ticker, interval="1d", period="5d")
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        cols[i].metric(name, f"{last_c:.2f}", f"{change:+.2f}%")
    else:
        cols[i].metric(name, "N/A", "Keine Daten")

st.divider()

# SEKTION 2: Einzelaktien-Analyse (H4 Momentum)
st.header("2. Momentum-Analyse (H4 Intervall)")

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    selected_idx = st.selectbox("Wähle einen Index:", list(STOCKS_BY_INDEX.keys()))
with col_sel2:
    selected_stock = st.selectbox("Wähle eine Aktie:", STOCKS_BY_INDEX[selected_idx])

if selected_stock:
    # H4 Daten laden (Yahoo liefert H4 meist nur für max 60 Tage)
    stock_data = get_market_data(selected_stock, interval="4h", period="60d")
    
    if not stock_data.empty:
        # Momentum Berechnung (z.B. Preis-Differenz über 14 Perioden auf H4)
        stock_data['Momentum'] = stock_data['Close'] - stock_data['Close'].shift(14)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader(f"Chart & Momentum: {selected_stock}")
            st.line_chart(stock_data['Close'])
            st.caption("Momentum Indikator (H4 - 14 Perioden)")
            st.area_chart(stock_data['Momentum'])
            
        with c2:
            st.subheader("Monte Carlo (30 Tage)")
            # Simulation starten
            sim_results = run_monte_carlo(stock_data)
            
            fig, ax = plt.subplots(figsize=(10, 7))
            ax.plot(sim_results, color='royalblue', alpha=0.05) # Viele Pfade blass
            ax.plot(sim_results.mean(axis=1), color='red', linewidth=2, label='Mittelwert')
            ax.set_title(f"Simulation für {selected_stock}")
            ax.set_xlabel("Tage in die Zukunft")
            ax.set_ylabel("Kurs")
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            
            # Statistisches Kursziel
            target_price = sim_results.mean(axis=1).iloc[-1]
            st.metric("Erwarteter Kurs (30d)", f"{target_price:.2f}")
    else:
        st.error(f"Konnte keine H4-Daten für {selected_stock} abrufen.")

# Footer
st.divider()
st.caption("Datenquelle: Yahoo Finance API. Intervall: H4 (4 Stunden) / D (Tag).")
