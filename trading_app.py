import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="Pro Monitor", layout="wide")

# --- HEADER: ZEIT & DATUM ---
jetzt = datetime.now()
st.title("📊 Profi Trading Dashboard")
st.subheader(f"🕒 {jetzt.strftime('%A, %d.%m.%Y | %H:%M:%S')} Uhr")

# --- TICKER LISTE ---
tickers = {
    "EUR/USD": "EURUSD=X",
    "DAX": "^GDAXI",
    "NASDAQ 100": "^NDX",
    "S&P 1000": "^SP1000"
}

def get_extended_data():
    results = []
    for name, symbol in tickers.items():
        try:
            t = yf.Ticker(symbol)
            # Wir brauchen mehr Daten für ATR (z.B. 20 Tage)
            df = t.history(period="1mo")
            if len(df) > 15:
                current = df['Close'].iloc[-1]
                
                # 1. ROC (Rate of Change - 10 Tage)
                roc = ((current - df['Close'].iloc[-10]) / df['Close'].iloc[-10]) * 100
                
                # 2. ATR (Average True Range - vereinfacht über High/Low)
                df['TR'] = df['High'] - df['Low']
                atr = df['TR'].rolling(window=14).mean().iloc[-1]
                
                # 3. RS (Relative Strength zum S&P 500 / NASDAQ)
                # Hier nehmen wir vereinfacht die Performance im Vergleich zum Vortag
                rs = (df['Close'].pct_change().iloc[-1]) * 100

                # Formatierung
                val = f"{current:.8f}" if "USD" in name else f"{current:,.2f}"
                
                results.append({
                    "Asset": name, "Kurs": val, 
                    "ATR": f"{atr:.4f}", "RS": f"{rs:.2%}", "ROC": f"{roc:.2f}%"
                })
        except:
            continue
    return results

data = get_extended_data()

# --- LAYOUT MIT EXPANDERN ---
for item in data:
    with st.expander(f"🔍 Details für {item['Asset']} (Kurs: {item['Kurs']})"):
        col1, col2, col3 = st.columns(3)
        # ATR: Zeigt die tägliche Schwankungsbreite (Volatilität)
        col1.metric("ATR (14d)", item['ATR'], help="Average True Range - Maß für Volatilität")
        # RS: Relative Stärke (Momentum zum Vortag)
        col2.metric("RS (Momentum)", item['RS'], help="Relative Stärke / Tagesänderung")
        # ROC: Kursänderungsrate über 10 Tage
        col3.metric("ROC (10d)", item['ROC'], help="Rate of Change - Dynamik des Trends")

# Automatisches Update
time.sleep(60)
st.rerun()
