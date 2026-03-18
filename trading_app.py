import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. FUNKTIONEN (Müssen ganz oben stehen!) ---

def get_market_data(ticker, interval="1d", period="60d"):
    """Lädt Marktdaten sicher von Yahoo Finance."""
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        # Fix für MultiIndex Spalten bei neueren yfinance Versionen
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
    # Hier wird die Funktion aufgerufen, die nun oben definiert ist
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
            # Indizes: 2 Stellen
            val_str = f"{last_c:.2f}"

        # Anzeige untereinander ohne Emojis oder Infoboxen
        st.write(f"**{name}**")
        st.write(f"Kurs: {val_str} | Änderung: {change:+.2f}%")
        st.divider()
    else:
        st.write(f"**{name}**")
        st.write("Kursdaten derzeit nicht verfügbar")
        st.divider()

# --- 4. AKTIEN-ANALYSE DAX & NASDAQ ---
# (Hier kannst du deinen Code für H4 Momentum und Monte Carlo anschließen)
