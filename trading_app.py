import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. FUNKTION ZUERST DEFINIEREN ---
def get_market_data(ticker, interval="1d", period="5d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        # Fix für neue yfinance Versionen
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except:
        return pd.DataFrame()

# --- 2. ANZEIGE-LOGIK ---
st.header("1. Globales Markt-Framework")

SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", "EUR/RUB": "EURRUB=X", 
    "DAX Index": "^GDAXI", "EuroStoxx 50": "^STOXX50E", 
    "Nifty 50": "^NSEI", "BIST 100": "XU100.IS"
}

for name, ticker in SYMBOLS_GENERAL.items():
    df_gen = get_market_data(ticker)
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        
        # Logik für Nachkommastellen: 
        # Wenn "/" im Namen (Währung), dann 5 Stellen, sonst 2.
        if "/" in name:
            val_str = f"{last_c:.5f}"
        else:
            val_str = f"{last_c:.2f}"

        # Anzeige untereinander ohne Symbole
        st.write(f"**{name}**")
        st.write(f"Kurs: {val_str} | Änderung: {change:+.2f}%")
        st.divider()
