import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. FUNKTION GANZ OBEN DEFINIEREN (Behebt den NameError) ---
def get_market_data(ticker, interval="1d", period="5d"):
    try:
        # Progress=False verhindert unnötige Log-Fehler in Streamlit
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        # Spalten für neue yfinance Versionen fixieren
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return pd.DataFrame()

# --- 2. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor", layout="centered")

SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", 
    "EUR/RUB": "EURRUB=X", 
    "DAX Index": "^GDAXI", 
    "EuroStoxx 50": "^STOXX50E", 
    "Nifty 50": "^NSEI", 
    "BIST 100": "XU100.IS"
}

# --- 3. ANZEIGE MARKT-FRAMEWORK ---
st.header("1. Globales Markt-Framework")

for name, ticker in SYMBOLS_GENERAL.items():
    # Aufruf der oben definierten Funktion
    df_gen = get_market_data(ticker)
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        
        # LOGIK FÜR NACHKOMMASTELLEN
        # Währungen (enthalten '/') -> 5 Stellen
        # Alle anderen (Indices) -> 2 Stellen
        if "/" in name:
            val_str = f"{last_c:.5f}"
        else:
            val_str = f"{last_c:.2f}"

        # Schlichte Anzeige untereinander
        st.write(f"**{name}**")
        st.write(f"Kurs: {val_str} | Änderung: {change:+.2f}%")
        st.divider()
    else:
        st.write(f"**{name}**")
        st.write("Kursdaten derzeit nicht verfügbar")
        st.divider()

# --- 4. AKTIEN-AUSWAHL DAX & NASDAQ ---
# Hier kannst du deine Einzeltitel-Logik (H4 Momentum) anschließen
