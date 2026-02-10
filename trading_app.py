import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Pro Trading Monitor", layout="wide")

# --- HEADER ---
jetzt = datetime.now()
st.title(f"📊 Trading Dashboard | {jetzt.strftime('%A, %d.%m.%Y | %H:%M:%S')} Uhr")

# Ticker-Definition
tickers = {"EUR/USD": "EURUSD=X", "DAX": "^GDAXI", "NASDAQ 100": "^NDX"}

def get_data():
    results = {}
    for name, symbol in tickers.items():
        t = yf.Ticker(symbol)
        df = t.history(period="1mo")
        if not df.empty:
            current = df['Close'].iloc[-1]
            # 10/90 Logik & Wetter [cite: 2026-02-07]
            low, high = df['Low'].min(), df['High'].max()
            pos = ((current - low) / (high - low)) * 100
            
            # Wetter-Logik & Farben
            if pos > 90: icon, color = "☀️", "red"  # Extrem Hoch
            elif pos < 10: icon, color = "⛈️", "green" # Extrem Tief
            else: icon, color = "⛅", "white" # Normal
            
            # ATR, ROC, RS
            df['TR'] = df['High'] - df['Low']
            atr = df['TR'].rolling(window=14).mean().iloc[-1]
            roc = ((current - df['Close'].iloc[-10]) / df['Close'].iloc[-10]) * 100
            
            results[name] = {
                "val": f"{current:.8f}" if "USD" in name else f"{current:,.2f}",
                "pos": pos, "icon": icon, "color": color, "atr": atr, "roc": roc
            }
    return results

data = get_data()

# --- LAYOUT OBEN: HAUPTWERTE ---
cols = st.columns(len(data))
for i, (name, d) in enumerate(data.items()):
    with cols[i]:
        st.markdown(f"### {d['icon']} {name}")
        st.markdown(f"## :{d['color']}[{d['val']}]")

st.divider()

# --- LAYOUT MITTE: INDIKATOREN ---
st.write("### 📈 Technische Indikatoren")
ind_cols = st.columns(3)
for i, (name, d) in enumerate(data.items()):
    with ind_cols[i]:
        st.info(f"**{name}**")
        st.metric("ATR (14d)", f"{d['atr']:.4f}")
        st.metric("ROC (10d)", f"{d['roc']:.2f}%", delta=f"{d['roc']:.2f}%")

# --- LAYOUT UNTEN: SLIDER & ERKLÄRUNG ---
with st.expander("ℹ️ Erklärung der Werte & Indikatoren"):
    st.write("**10%/90% Regel:** Grün/Sturm bedeutet Tiefstand (<10%), Rot/Sonne bedeutet Hochstand (>90%) [cite: 2026-02-07].")
    st.write("**ATR:** Zeigt die tägliche Volatilität an.")
    st.write("**ROC:** Misst die Geschwindigkeit der Kursbewegung über 10 Tage.")
    st.write("**Wetter:** ☀️ = Markt heiß gelaufen, ⛈️ = Kaufchance/Tief, ⛅ = Normalbereich.")
