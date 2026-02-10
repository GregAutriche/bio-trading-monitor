import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Trading Monitor", layout="wide")

st.title("📊 Dein Trading & China-Exposure Monitor")

# Ticker Definition
tickers = {
    "EUR/USD": "EURUSD=X",
    "DAX": "^GDAXI",
    "NASDAQ 100": "^NDX",
    "S&P 1000": "^SP1000"
}

def get_data():
    results = []
    for name, symbol in tickers.items():
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y")
        
        if not hist.empty:
            current = hist['Close'].iloc[-1]
            low_52w = hist['Low'].min()
            high_52w = hist['High'].max()
            
            # 10% / 90% Logik
            pos = ((current - low_52w) / (high_52w - low_52w)) * 100
            
            if pos > 90: status = "🔴 Extrem Hoch (>90%)"
            elif pos < 10: status = "🟢 Extrem Tief (<10%)"
            else: status = "⚪ Normalbereich"
            
            # Formatierung: Dollar mit 8 Stellen, Indizes mit 2
            val_str = f"{current:.8f}" if name == "EUR/USD" else f"{current:,.2f}"
            
            results.append({"Asset": name, "Wert": val_str, "Bereich": status})
    return pd.DataFrame(results)

data_df = get_data()
st.table(data_df)

st.info("Hinweis: DAX-Werte mit hoher China-Exposition (VW, BASF, SAP) manuell im Auge behalten.")
