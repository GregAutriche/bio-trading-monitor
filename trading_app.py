import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURATION & TICKER ---
st.set_page_config(page_title="Trading & Bio Monitor", layout="wide")

# Ticker-Konfiguration mit deinen Default-Werten
meine_ticker = {
    "EUR/USD": {"symbol": "EURUSD=X", "default": 1.1778, "datum": "06.02. 00:00"},
    "DAX Index": {"symbol": "^GDAXI", "default": 24721.46, "datum": "06.02. 00:00"},
    "NASDAQ 100": {"symbol": "^IXIC", "default": 23031.21, "datum": "06.02. 00:00"}
}

# --- 2. FUNKTIONEN FÜR INDIKATOREN (ATR & RSI) ---
def berechne_indikatoren(symbol):
    try:
        data = yf.download(symbol, period="30d", interval="1d", progress=False)
        if data.empty: return "N/A", "N/A"
        
        # RSI Berechnung (14 Tage)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # ATR Berechnung (14 Tage)
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        
        return f"{atr.iloc[-1]:.2f}", f"{rsi.iloc[-1]:.1f}"
    except:
        return "N/A", "N/A"

def hole_status_und_daten(info):
    try:
        t = yf.Ticker(info["symbol"])
        df = t.history(period="1d")
        if not df.empty and df.index[-1].date() == datetime.now().date():
            return df['Close'].iloc[-1], df.index[-1].strftime('%d.%m. %H:%M'), True
        return info["default"], info["datum"], False
    except:
        return info["default"], info["datum"], False

# --- 3. HEADER & METRIKEN MIT WETTERBERICHT ---
st.title("📊 Dein Trading- & Bio-Monitor")
cols = st.columns(len(meine_ticker))
ist_live = False

for i, (name, info) in enumerate(meine_ticker.items()):
    preis, zeit, live = hole_status_und_daten(info)
    if live: ist_live = True
    atr, rsi = berechne_indikatoren(info["symbol"])
    
    with cols[i]:
        format_str = "{:.4f}" if "USD" in name else "{:,.2f}"
        st.metric(label=name, value=format_str.format(preis))
        st.caption(f"☁️ ATR: {atr} | 🌡️ RSI: {rsi}") # Dein "Wetterbericht"
        status_label = ":green[[data]]" if live else ":red[[no data]]"
        st.write(f"{zeit} {status_label}")

st.divider()

# --- 4. MARKT-CHECK & BEWERTUNGSSKALA ---
global_status = ":green[[data]]" if ist_live else ":red[[no data]]"
st.subheader(f"📈 Markt-Check & China-Exposure Logik {global_status}")
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

st.write(f"### Bewertungsskala: {global_status}")
l, m, r = st.columns(3)

# NEUTRALE LOGIK: Wenn [no data], dann alle Boxen blau/grau mit farbigen Punkten
with l:
    if ist_live and wert < 10:
        st.error("🔴 **EXTREM TIEF**\n\nStatus: AKTIV")
    else:
        st.write("🔴 **Extrem Tief**")
        st.info("Möglichkeit: < 10%")

with m:
    if ist_live and 10 <= wert <= 90:
        st.success("🟢 **Normalbereich**\n\nStatus: AKTIV")
    else:
        st.write("🟢 **Normalbereich**")
        st.info("Möglichkeit: 10% - 90%")

with r:
    if ist_live and wert > 90:
        st.error("🔴 **EXTREM HOCH**\n\nStatus: AKTIV")
    else:
        st.write("🟣 **Extrem Hoch**")
        st.info("Möglichkeit: > 90%")

st.divider()

# --- 5. BIO-BACKUP & ROUTINEN ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: **05 bis 08 Minuten**")
    st.warning("**Sicherheitsregel:** Gleichmäßig atmen! Keine Preßatmung!")
    st.write("* **Blutdruck:** Senkung durch Sprossen und Rote Bete.")
    st.write("* **Warnung:** Keine Mundspülungen mit Chlorhexidin.")
    st.write("* **Zähne:** Nicht unmittelbar nach dem Essen putzen.")

with st.expander("✈️ Reisen & Ernährung"):
    st.write(f"* **Ticket:** Österreich Ticket vorhanden.")
    st.write("* **Snacks:** Nüsse für die Reise einplanen.")
    st.write("* **Vorsicht:** Grapefruit-Wechselwirkungen beachten.")
