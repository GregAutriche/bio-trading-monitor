import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. VERSIONEN ANZEIGEN (Ganz oben zur Diagnose) ---
st.sidebar.write(f"Streamlit Version: {st.__version__}")
st.sidebar.write(f"Pandas Version: {pd.__version__}")
st.sidebar.write(f"Yfinance Version: {yf.__version__}")

# --- 2. FUNKTIONEN (MUSS vor dem Aufruf stehen!) ---

def get_market_data(ticker, interval="1d", period="60d"):
    """Lädt Marktdaten sicher von Yahoo Finance."""
    try:
        # progress=False verhindert Log-Fehler in Streamlit
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        # Fix für MultiIndex Spalten bei neueren yfinance Versionen
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception as e:
        st.error(f"Fehler beim Laden von {ticker}: {e}")
        return pd.DataFrame()

# --- 3. KONFIGURATION & MARKT-ÜBERSICHT ---

st.set_page_config(page_title="Bio-Trading Monitor", layout="centered")

SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", 
    "EUR/RUB": "EURRUB=X", 
    "DAX Index": "^GDAXI", 
    "EuroStoxx 50": "^STOXX50E", 
    "Nifty 50": "^NSEI", 
    "BIST 100": "XU100.IS"
}

st.header("1. Globales Markt-Framework")

for name, ticker in SYMBOLS_GENERAL.items():
    # Jetzt ist die Funktion oben definiert und wird hier gefunden
    df_gen = get_market_data(ticker, interval="1d", period="5d")
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        
        # LOGIK FÜR NACHKOMMASTELLEN
        # Währungen (haben ein '/') -> 5 Stellen
        # Alles andere (Indices) -> 2 Stellen
        if "/" in name:
            val_str = f"{last_c:.5f}"
        else:
            val_str = f"{last_c:.2f}"

        st.write(f"**{name}**")
        st.write(f"Kurs: {val_str} | Änderung: {change:+.2f}%")
        st.divider()
    else:
        st.write(f"**{name}**")
        st.write("Daten derzeit nicht verfügbar")
        st.divider()

# --- 4. AKTIEN-AUSWAHL (Top 7) ---
# (Hier folgt dein weiterer Code für H4 Momentum und Monte Carlo)
