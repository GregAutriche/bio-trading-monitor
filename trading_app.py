import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. FUNKTIONEN DEFINIEREN (Muss VOR dem Aufruf stehen) ---

def get_market_data(ticker, interval="1d", period="5d"):
    """Lädt Marktdaten von Yahoo Finance."""
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        return data
    except Exception:
        return pd.DataFrame()

# --- 2. KONFIGURATION ---

st.set_page_config(page_title="Bio-Trading Monitor", layout="centered")

SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", 
    "EUR/RUB": "EURRUB=X", 
    "DAX": "^GDAXI", 
    "EuroStoxx": "^STOXX50E", 
    "Nifty": "^NSEI", 
    "BIST100": "XU100.IS"
}

# --- 3. ANZEIGE MARKT-FRAMEWORK ---

st.header("1. Globales Markt-Framework")

for name, ticker in SYMBOLS_GENERAL.items():
    # Hier wird die oben definierte Funktion aufgerufen
    df_gen = get_market_data(ticker, interval="1d", period="5d")
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        
        # Währungen 5 Stellen, sonst 2 Stellen
        is_fx = "/" in name or "X" in ticker
        val_str = f"{last_c:.5f}" if is_fx else f"{last_c:,.2f}"

        # Schlichte Textanzeige untereinander
        st.write(f"**{name}**")
        st.write(f"Kurs: {val_str} | Änderung: {change:+.2f}%")
        st.divider()
    else:
        st.write(f"**{name}**")
        st.write("Keine aktuellen Daten verfügbar")
        st.divider()

# --- 4. H4 MOMENTUM & MONTE CARLO ---
# (Füge hier deine weiteren Analysen für Einzelaktien ein)
