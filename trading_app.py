import streamlit as st
import yfinance as yf
import pandas as pd

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

st.title("📊 Marktüberblick")
st.markdown("---")

# --- Marktdaten untereinander anzeigen ---
for name, ticker in SYMBOLS_GENERAL.items():
    # Daten abrufen
    df_gen = yf.download(ticker, period="5d", interval="1d", progress=False)
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        
        # Formatierung: Währungen mit 5 Nachkommastellen, Indizes mit 2
        if "/" in name or "USD" in ticker or "X" in ticker:
            val_str = f"{last_c:.5f}"
        else:
            val_str = f"{last_c:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # Anzeige als Metrik (untereinander durch einfachen Aufruf)
        st.metric(
            label=name, 
            value=val_str, 
            delta=f"{change:+.2f}%"
        )
        st.markdown("---") # Trennlinie für bessere Lesbarkeit untereinander
    else:
        st.metric(label=name, value="N/A", delta="Keine Daten")
        st.markdown("---")

# Der Rest deines Codes (Momentum / Monte Carlo) folgt hier...
