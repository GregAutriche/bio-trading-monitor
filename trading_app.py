import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Pro Trading Monitor", layout="wide")

# --- HEADER: Datum & Uhrzeit ---
jetzt = datetime.now()
st.markdown(f"## 🕒 {jetzt.strftime('%d.%m.%Y | %H:%M:%S')} Uhr")

# Ticker-Liste (Inklusive S&P 1000)
tickers = {
    "EUR/USD": "EURUSD=X", 
    "DAX": "^GDAXI", 
    "NASDAQ 100": "^NDX",
    "S&P 1000": "^SP1000"
}

def get_market_data():
    res = {}
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            df = t.history(period="1mo")
            if not df.empty:
                curr = df['Close'].iloc[-1]
                low, high = df['Low'].min(), df['High'].max()
                pos = ((curr - low) / (high - low)) * 100
                
                # Wetter & Farblogik [cite: 2026-02-07]
                if pos > 90: icon, color = "☀️", "red"
                elif pos < 10: icon, color = "⛈️", "green"
                else: icon, color = "⛅", "orange" # Gelb/Orange für Normal
                
                # Indikatoren
                df['TR'] = df['High'] - df['Low']
                atr = df['TR'].rolling(window=14).mean().iloc[-1]
                roc = ((curr - df['Close'].iloc[-10]) / df['Close'].iloc[-10]) * 100
                
                res[name] = {
                    "kurs": f"{curr:.8f}" if "USD" in name else f"{curr:,.2f}",
                    "icon": icon, "color": color, "atr": atr, "roc": roc
                }
        except: continue
    return res

data = get_market_data()

# --- REINE WERTE OBEN ---
cols = st.columns(len(data))
for i, (name, d) in enumerate(data.items()):
    with cols[i]:
        st.markdown(f"### {d['icon']} {name}")
        # Hier wird der Kurs direkt in der Farbe angezeigt
        st.markdown(f"<h2 style='color:{d['color']};'>{d['kurs']}</h2>", unsafe_allow_html=True)

st.divider()

# --- INDIKATOREN DARUNTER ---
st.write("### 📈 Technische Indikatoren (ATR / ROC)")
ind_cols = st.columns(len(data))
for i, (name, d) in enumerate(data.items()):
    with ind_cols[i]:
        st.metric(f"ATR {name}", f"{d['atr']:.4f}")
        st.metric(f"ROC {name}", f"{d['roc']:.2f}%")

# --- SLIDER / ERKLÄRUNG GANZ UNTEN ---
with st.expander("ℹ️ Erklärung & Hilfe"):
    st.write("**Wetter-Symbole:** Zeigen die 10/90 Regel. ⛈️ = Tief (<10%), ☀️ = Hoch (>90%) [cite: 2026-02-07].")
    st.write("**Farben:** Grün bedeutet günstig, Rot bedeutet teuer.")
