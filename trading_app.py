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
        
        cp = hist['Close'].iloc[-1]
        lo, hi = hist['Low'].min(), hist['High'].max()
        pos_percent = ((cp - lo) / (hi - lo)) * 100
        
        # RSI & ATR Berechnung (Live)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        rsi_val = 100 - (100 / (1 + rs.iloc[-1]))
        atr_val = (hist['High'] - hist['Low']).rolling(window=14).mean().iloc[-1]
        
        status = "NORMAL"
        trend = "🟡"
        if pos_percent < 10: status, trend = "EXTREM TIEF", "🔴"
        elif pos_percent > 90: status, trend = "EXTREM HOCH", "🟢"
            
        return {"Preis": cp, "Pos": pos_percent, "RSI": rsi_val, "ATR": atr_val, "Status": status, "Trend": trend}
    except:
        return None

# 3. HEADER & INFORMATIONS-SLIDER
st.title(f"🚀 KONTROLLTURM AKTIV | {now.strftime('%d.%m.%Y | %H:%M:%S')}")

st.subheader("Informationsquelle: Parameter-Definitionen")
info = st.select_slider(
    'Was bedeuten die Spalten?',
    options=['ATR Definition', 'RSI Definition', 'ROI Definition', '10/90 Regel']
)

if info == 'ATR Definition':
    st.info("**ATR (Average True Range):** Zeigt die Schwankungsbreite der letzten 14 Tage.")
elif info == 'RSI Definition':
    st.info("**RSI (Relative Strength Index):** Überkauft (>70) oder Überverkauft (<30).")
elif info == 'ROI Definition':
    st.info("**ROI (Rate of Change):** Misst die prozentuale Kursdynamik der letzten 14 Tage.")
else:
    st.info("**10/90 Regel:** Kursstand im 52-Wochen-Kanal. <10% = Extrem Tief, >90% = Extrem Hoch.")

# 4. GESUNDHEITS-BACKUP (Wandsitz etc.)
st.warning("""
**Wichtige tägliche Regeln:** 1. **Wandsitz:** Täglich, aber **KEINE Pressatmung**!
2. **Ernährung:** Sprossen & Rote Bete (Blutdruck). Keine Phosphate/Grapefruit.
3. **Hygiene:** Kein Chlorhexidin, kein Kaugummi, Zähneputzen mit Abstand zum Essen.
""")

st.divider()

# 5. DIE 14 CHAMPIONS (Zurück auf volle Stärke)
col1, col2 = st.columns(2)

eu_champs = [
    {"ticker": "OTP.BU", "name": "OTP Bank"}, {"ticker": "BAS.DE", "name": "BASF"},
    {"ticker": "SIE.DE", "name": "Siemens"}, {"ticker": "VOW3.DE", "name": "VW"},
    {"ticker": "SAP.DE", "name": "SAP"}, {"ticker": "ADS.DE", "name": "Adidas"},
    {"ticker": "BMW.DE", "name": "BMW"}
]

us_champs = [
    {"ticker": "STLD", "name": "Steel Dynamics"}, {"ticker": "WMS", "name": "Adv. Drainage"},
    {"ticker": "NVDA", "name": "Nvidia"}, {"ticker": "AAPL", "name": "Apple"},
    {"ticker": "MSFT", "name": "Microsoft"}, {"ticker": "GOOGL", "name": "Google"},
    {"ticker": "AMZN", "name": "Amazon"}
]

def build_view(stocks):
    rows = []
    for s in stocks:
        m = fetch_live_metrics(s['ticker'])
        if m:
            rows.append({"Trend": m['Trend'], "Name": s['name'], "Live-Preis": f"{m['Preis']:.2f}",
                         "Pos %": f"{m['Pos']:.1f}%", "RSI": f"{m['RSI']:.1f}", "Status": m['Status']})
    return pd.DataFrame(rows)

with col1:
    st.subheader("Europa Champions (Live gezogen)")
    st.table(build_view(eu_champs))

with col2:
    st.subheader("USA Hidden Champions (Live gezogen)")
    st.table(build_view(us_champs))
