import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import locale

# Versuche deutsche Zeitformatierung zu setzen
try:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
except:
    pass # Fallback auf Standard, falls de_DE nicht auf dem Server ist

st.set_page_config(page_title="Trading Monitor", layout="wide")

# --- ZEIT- UND DATUMSANZEIGE ---
jetzt = datetime.now()
wochentag = jetzt.strftime("%A")
datum = jetzt.strftime("%d.%m.%Y")
uhrzeit = jetzt.strftime("%H:%M:%S")

st.title(f"📊 Trading Monitor")
st.subheader(f"Heute ist {wochentag}, der {datum} | {uhrzeit} Uhr")

# --- FINANZDATEN ---
tickers = {
    "EUR/USD": "EURUSD=X",
    "DAX": "^GDAXI",
    "NASDAQ 100": "^NDX",
    "S&P 1000": "^SP1000"
}

def get_data():
    results = []
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                # Deine 10/90 Regel Logik
                low_52w, high_52w = hist['Low'].min(), hist['High'].max()
                pos = ((current - low_52w) / (high_52w - low_52w)) * 100
                
                status = "🔴 EXTREM HOCH" if pos > 90 else "🟢 EXTREM TIEF" if pos < 10 else "⚪ Normal"
                val_str = f"{current:.8f}" if name == "EUR/USD" else f"{current:,.2f}"
                results.append({"Asset": name, "Wert": val_str, "Status": status})
        except:
            continue
    return pd.DataFrame(results)

st.table(get_data())
