import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Konfiguration der Seite
st.set_page_config(page_title="Bio-Trading App", layout="wide", initial_sidebar_state="expanded")

# --- GESUNDHEITS-LOGIK ---
if 'next_check' not in st.session_state:
    st.session_state.next_check = datetime.now() + timedelta(minutes=10)

# --- SIDEBAR (DEIN GESUNDHEITS-ZENTRUM) ---
with st.sidebar:
    st.title("🧘 Health-Check")
    st.write(f"Nächster Wandsitz um: *{st.session_state.next_check.strftime('%H:%M:%S')}*")
    
    if st.button("✅ Wandsitz erledigt!"):
        st.session_state.next_check = datetime.now() + timedelta(minutes=10)
        st.success("Super! Blutdruck gesenkt.")

    st.divider()
    st.markdown("### 🥗 Ernährungstipps")
    st.info("• Sprossen & Rote Bete bereit?\n• Keine Mundspülung nach Training!")
    st.markdown("### 🚅 Unterwegs")
    st.write("Österreich Ticket dabei? Nutze die Zugfahrt für Atemübungen.")

# --- DATEN-FUNKTION ---
def get_market_data():
    symbols = {"EUR/USD": "EURUSD=X", "DAX": "^GDAXI", "NASDAQ": "^IXIC"}
    results = {}
    for name, sym in symbols.items():
        ticker = yf.Ticker(sym)
        df = ticker.history(period="1d", interval="1m")
        if not df.empty:
            last_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-60] if len(df) > 60 else last_price
            roc = ((last_price - prev_price) / prev_price) * 100
            
            # RSI Simulation (vereinfacht für die App)
            delta = df['Close'].diff()
            up = delta.where(delta > 0, 0).rolling(14).mean()
            down = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (up.iloc[-1] / down.iloc[-1])))
            
            results[name] = {"price": last_price, "roc": roc, "rsi": rsi}
    return results

# --- HAUPTSEITE ---
st.title("💹 Dein Bio-Trading Monitor")
data = get_market_data()

# Spalten-Layout
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("EUR/USD (Cyan Fokus)", f"{data['EUR/USD']['price']:.5f}", f"{data['EUR/USD']['roc']:.2f}%")
    st.write("Währungstrend")

with c2:
    val = data['DAX']['price']
    rsi_dax = data['DAX']['rsi']
    st.metric("DAX Index", f"{val:,.2f} pkt")
    # RSI Anzeige mit Farblogik
    if rsi_dax > 70: st.markdown(f"RSI: <span style='color:purple; font-weight:bold'>{rsi_dax:.2f} (HEISS)</span>", unsafe_allow_html=True)
    elif rsi_dax < 30: st.markdown(f"RSI: <span style='color:orange; font-weight:bold'>{rsi_dax:.2f} (KALT)</span>", unsafe_allow_html=True)
    else: st.write(f"RSI: {rsi_dax:.2f} (Neutral)")

with c3:
    st.metric("NASDAQ 100", f"{data['NASDAQ']['price']:,.2f}", f"{data['NASDAQ']['roc']:.2f}%")
    st.write("Wetter: ⛈️ Gewitter")

# Divergenz-Check
st.divider()
if data['EUR/USD']['roc'] > 0.05 and data['NASDAQ']['roc'] < -0.3:
    st.error("🚨 DIVERGENZ-ALARM: Dollar steigt & Nasdaq fällt!")
else:
    st.success("✅ Markt-Synchronität ist stabil.")