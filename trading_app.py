import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz

# 1. SETUP
st.set_page_config(page_title="Kontrollturm Aktiv", layout="wide")
local_tz = pytz.timezone('Europe/Berlin')
now = datetime.now(local_tz)

# --- DYNAMISCHE RECHEN-ENGINE (Zieht alles live) ---
@st.cache_data(ttl=60)
def fetch_live_metrics(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1y")
        if len(hist) < 20: return None
        
        # Aktueller Kurs
        cp = hist['Close'].iloc[-1]
        
        # 10/90 Position (Dynamisch berechnet)
        lo, hi = hist['Low'].min(), hist['High'].max()
        pos_percent = ((cp - lo) / (hi - lo)) * 100
        
        # RSI (Dynamisch berechnet)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        rsi_val = 100 - (100 / (1 + rs.iloc[-1]))
        
        # ATR (Dynamisch berechnet)
        atr_val = (hist['High'] - hist['Low']).rolling(window=14).mean().iloc[-1]
        
        # Trend-Logik nach deiner Regel
        status = "NORMAL"
        trend = "🟡"
        if pos_percent < 10: status, trend = "EXTREM TIEF", "🔴"
        elif pos_percent > 90: status, trend = "EXTREM HOCH", "🟢"
            
        return {"Preis": cp, "Pos": pos_percent, "RSI": rsi_val, "ATR": atr_val, "Status": status, "Trend": trend}
    except:
        return None

# 2. HEADER & INFORMATIONSSÄULE (Slider)
st.title(f"🚀 KONTROLLTURM AKTIV | {now.strftime('%d.%m.%Y | %H:%M')}")

st.subheader("Informationsquelle: Parameter-Definitionen")
info = st.select_slider(
    'Was bedeuten die Spalten in der Tabelle?',
    options=['ATR Definition', 'RSI Definition', '10/90 Regel']
)

if info == 'ATR Definition':
    st.info("**ATR:** Misst die Volatilität (Schwankungsbreite). Je höher, desto nervöser das Asset.")
elif info == 'RSI Definition':
    st.info("**RSI:** Zeigt die relative Stärke. < 30 bedeutet 'ausverkauft' (Chance), > 70 bedeutet 'heißgelaufen' (Gefahr).")
else:
    st.info("**10/90 Regel:** Kursstand im Vergleich zum 52-Wochen-Hoch/Tief. Deine Alarm-Zone für Extreme.")

# 3. GESUNDHEITS-BACKUP (Immer präsent)
st.warning("""
**Wichtige tägliche Regeln:** 1. **Wandsitz:** Täglich ausführen, aber **KEINE Pressatmung** (Luft nicht anhalten!).
2. **Ernährung:** Sprossen & Rote Bete (Blutdruck). Keine Phosphate & Grapefruit.
3. **Hygiene:** Kein Chlorhexidin (Mundspülung), kein Kaugummi.
""")

st.divider()

# 4. CHAMPIONS (Nur Ticker-Listen, keine festen Werte!)
col1, col2 = st.columns(2)

# Nur die Basis-Identität der Aktien hinterlegen
europa_champions = [
    {"ticker": "OTP.BU", "name": "OTP Bank"},
    {"ticker": "BAS.DE", "name": "BASF"},
    {"ticker": "SIE.DE", "name": "Siemens"},
    {"ticker": "VOW3.DE", "name": "VW"}
]

usa_champions = [
    {"ticker": "STLD", "name": "Steel Dynamics"},
    {"ticker": "WMS", "name": "Advanced Drainage"},
    {"ticker": "NVDA", "name": "Nvidia"}
]

def build_dynamic_view(stocks):
    final_rows = []
    for s in stocks:
        m = fetch_live_metrics(s['ticker'])
        if m:
            final_rows.append({
                "Trend": m['Trend'],
                "Name": s['name'],
                "Live-Preis": f"{m['Preis']:.2f}",
                "Pos %": f"{m['Pos']:.1f}%",
                "RSI": f"{m['RSI']:.1f}",
                "ATR": f"{m['ATR']:.2f}",
                "Status": m['Status']
            })
    return pd.DataFrame(final_rows)

with col1:
    st.subheader("Europa Champions (Live gezogen)")
    st.table(build_dynamic_view(europa_champions))

with col2:
    st.subheader("USA Hidden Champions (Live gezogen)")
    st.table(build_dynamic_view(usa_champions))
