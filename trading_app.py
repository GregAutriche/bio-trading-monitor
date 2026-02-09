import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz

# Sicherer Import für Auto-Refresh
HAS_AUTO = False
try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTO = True
except Exception:
    pass

# 1. SETUP
st.set_page_config(page_title="Kontrollturm Aktiv", layout="wide")

# Auto-Refresh nur starten, wenn das Paket wirklich geladen wurde
if HAS_AUTO:
    st_autorefresh(interval=300000, key="datarefresh")

local_tz = pytz.timezone('Europe/Berlin')
now = datetime.now(local_tz)

# --- DYNAMISCHE RECHEN-ENGINE ---
@st.cache_data(ttl=60)
def fetch_live_metrics(ticker_symbol, is_currency=False):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1y")
        if len(hist) < 20: return None
        
        cp = hist['Close'].iloc[-1]
        lo, hi = hist['Low'].min(), hist['High'].max()
        pos_percent = ((cp - lo) / (hi - lo)) * 100
        
        # RSI Berechnung
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        rsi_val = 100 - (100 / (1 + rs.iloc[-1]))
        
        # Deine finale Symbol-Logik
        status = "NORMAL"
        icon = "🌿 🌳" 
        trend_dot = "🟡"
        
        if pos_percent < 10:
            status = "EXTREM TIEF"
            icon = "⚡" 
            trend_dot = "🔴"
        elif pos_percent > 90:
            status = "EXTREM HOCH"
            icon = "☀️" 
            trend_dot = "🟢"
            
        price_fmt = f"{cp:.4f}" if is_currency else f"{cp:,.0f}"
        return {"Preis": price_fmt, "Pos": pos_percent, "RSI": rsi_val, "Status": status, "Trend": trend_dot, "Icon": icon}
    except:
        return None

# --- DASHBOARD LAYOUT ---
st.title(f"🚀 KONTROLLTURM AKTIV | {now.strftime('%d.%m.%Y | %H:%M:%S')}")

cols_header = st.columns(3)
market_tickers = [("EUR/USD", "EURUSD=X", True), ("DAX Index", "^GDAXI", False), ("NASDAQ Composite", "^IXIC", False)]

for i, (label, sym, is_curr) in enumerate(market_tickers):
    m_data = fetch_live_metrics(sym, is_curr)
    if m_data:
        cols_header[i].metric(label, m_data['Preis'], f"{m_data['Pos']:.1f}% Position")

st.divider()

with st.expander("ℹ️ Informationsquelle: Symbol-Legende"):
    st.write("**🔴 + ⚡ (Extrem Tief < 10%):** Die Saat im Sturm.")
    st.write("**🌿 + 🌳 (Normal 10-90%):** Stabiles Wachstum (Gras & Baum).")
    st.write("**🟢 + ☀️ (Extrem Hoch > 90%):** Heiße Phase (Sonne).")

st.warning("⚠️ Wichtig: Wandsitz (KEINE Pressatmung!), Sprossen/Rote Bete, kein Chlorhexidin!")

st.divider()

# CHAMPIONS LISTE
eu_list = [{"t": "OTP.BU", "n": "OTP Bank"}, {"t": "BAS.DE", "n": "BASF"}, {"t": "SIE.DE", "n": "Siemens"}, {"t": "VOW3.DE", "n": "VW"}, {"t": "SAP.DE", "n": "SAP"}, {"t": "ADS.DE", "n": "Adidas"}, {"t": "BMW.DE", "n": "BMW"}]
us_list = [{"t": "STLD", "n": "Steel Dynamics"}, {"t": "WMS", "n": "Adv. Drainage"}, {"t": "NVDA", "n": "Nvidia"}, {"t": "AAPL", "n": "Apple"}, {"t": "MSFT", "n": "Microsoft"}, {"t": "GOOGL", "n": "Google"}, {"t": "AMZN", "n": "Amazon"}]

col1, col2 = st.columns(2)

def build_table(stocks):
    rows = []
    for s in stocks:
        d = fetch_live_metrics(s['t'])
        if d:
            rows.append({"Trend": d['Trend'], "Wetter": d['Icon'], "Name": s['n'], "Live": d['Preis'], "Pos%": f"{d['Pos']:.1f}%", "RSI": f"{d['RSI']:.1f}", "Status": d['Status']})
    st.table(pd.DataFrame(rows))

with col1:
    st.subheader("Europa Champions")
    build_table(eu_list)
with col2:
    st.subheader("USA Champions")
    build_table(us_list)
