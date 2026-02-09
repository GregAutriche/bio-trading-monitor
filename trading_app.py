import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz

# 1. SETUP & ZEIT (Korrekt für Wien/Berlin)
st.set_page_config(page_title="Kontrollturm Aktiv", layout="wide")
local_tz = pytz.timezone('Europe/Berlin')
now = datetime.now(local_tz)

# 2. DATEN-FUNKTION MIT CACHE (Aktualisiert alle 60 Sek)
@st.cache_data(ttl=60)
def get_market_data(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d", interval="1m")
    if hist.empty:
        return {"Preis": 0, "Trend": "⚪", "ROC": 0, "RSI": 50}
    
    current_price = hist['Close'].iloc[-1]
    # Einfache Logik für RSI/Trend Simulation (hier kommt deine echte Logik rein)
    return {
        "Name": symbol,
        "Preis": current_price,
        "Trend": "🟢" if hist['Close'].iloc[-1] > hist['Close'].iloc[0] else "🔴",
        "RSI": 55.0, # Platzhalter für deine Berechnung
        "ROC": 0.15  # Platzhalter
    }

# 3. HEADER (Jetzt synchron mit deiner Windows-Uhr)
st.title(f"🚀 KONTROLLTURM AKTIV | {now.strftime('%A, %d.%m.%Y | %H:%M:%S')}")

# 4. TOP INDIZES (EUR/USD, DAX, NASDAQ)
cols = st.columns(3)
indices = [("EUR/USD", "EURUSD=X"), ("DAX (ADR)", "EWG"), ("NASDAQ", "QQQ")]

for i, (label, sym) in enumerate(indices):
    data = get_market_data(sym)
    cols[i].metric(label, f"{data['Preis']:.4f}" if "USD" in label else f"{data['Preis']:.2f}")

st.divider()

# 5. DEINE 7 HIDDEN CHAMPIONS (EUROPA & USA)
champions_eu = ["ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE", "VOW3.DE", "BMW.DE"]
champions_us = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

col_eu, col_us = st.columns(2)

def show_champs(title, symbols):
    st.write(f"### {title}")
    rows = []
    for s in symbols:
        d = get_market_data(s)
        # Deine Logik: >90% Extrem Hoch, <10% Extrem Tief
        status = "NORMAL"
        if d['RSI'] > 90: status = "⚠️ EXTREM HOCH"
        if d['RSI'] < 10: status = "❄️ EXTREM TIEF"
        
        rows.append({"Trend": d['Trend'], "Name": s, "Preis(EUR)": f"{d['Preis']:.2f}", "Pos%": f"{d['RSI']}%", "Status": status})
    
    st.table(pd.DataFrame(rows))

with col_eu:
    show_champs("Europa: Deine 7 Hidden Champions", champions_eu)

with col_us:
    show_champs("USA: Deine 7 Hidden Champions", champions_us)

# 6. BACKUP INFOS & WANDSITZ
st.divider()
st.error(f"⚠️ **WANDSITZ:** Ruhig atmen! Keine Pressatmung (Blutdruck-Schutz)! [cite: 2025-12-20]")

with st.expander("📂 Backup-Infos (Gesundheit & Reisen)"):
    st.write("* **Reisen:** Nüsse einpacken. [cite: 2026-02-03]")
    st.write("* **Tickets:** Österreich Ticket vorhanden. [cite: 2026-01-25]")
    st.write("* **Blutdruck:** Rote Bete & Sprossen aktiv nutzen. [cite: 2025-12-20]")
