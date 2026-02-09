import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz

# Sicherer Import: Die App stürzt nicht ab, wenn das Modul fehlt
try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTO = True
except Exception:
    HAS_AUTO = False

st.set_page_config(page_title="Kontrollturm Aktiv", layout="wide")

# Refresh alle 5 Minuten, falls verfügbar
if HAS_AUTO:
    st_autorefresh(interval=300000, key="datarefresh")

local_tz = pytz.timezone('Europe/Berlin')
now = datetime.now(local_tz)

@st.cache_data(ttl=60)
def fetch_live_metrics(ticker_symbol, is_currency=False):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1y")
        if len(hist) < 20: return None
        cp = hist['Close'].iloc[-1]
        lo, hi = hist['Low'].min(), hist['High'].max()
        pos_percent = ((cp - lo) / (hi - lo)) * 100
        
        # RSI Logik
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        rsi_val = 100 - (100 / (1 + rs.iloc[-1]))
        
        # Deine gewünschten Symbole: Gras & Baum
        status, icon, trend_dot = "NORMAL", "🌿 🌳", "🟡"
        
        if pos_percent < 10:
            status, icon, trend_dot = "EXTREM TIEF", "⚡", "🔴"
        elif pos_percent > 90:
            status, icon, trend_dot = "EXTREM HOCH", "☀️", "🟢"
            
        price_fmt = f"{cp:.4f}" if is_currency else f"{cp:,.0f}"
        return {"Preis": price_fmt, "Pos": pos_percent, "RSI": rsi_val, "Status": status, "Trend": trend_dot, "Icon": icon}
    except:
        return None

st.title(f"🚀 KONTROLLTURM AKTIV | {now.strftime('%d.%m.%Y | %H:%M:%S')}")

# Markt-Metriken
cols = st.columns(3)
market_tickers = [("EUR/USD", "EURUSD=X", True), ("DAX Index", "^GDAXI", False), ("NASDAQ", "^IXIC", False)]
for i, (label, sym, is_curr) in enumerate(market_tickers):
    d = fetch_live_metrics(sym, is_curr)
    if d: cols[i].metric(label, d['Preis'], f"{d['Pos']:.1f}% Pos")

st.divider()
st.warning("⚠️ Wichtig: Wandsitz (KEINE Pressatmung!), Rote Bete, kein Chlorhexidin!")

# Champions Tabellen
eu_list = [{"t": "OTP.BU", "n": "OTP Bank"}, {"t": "BAS.DE", "n": "BASF"}, {"t": "SIE.DE", "n": "Siemens"}, {"t": "VOW3.DE", "n": "VW"}, {"t": "SAP.DE", "n": "SAP"}, {"t": "ADS.DE", "n": "Adidas"}, {"t": "BMW.DE", "n": "BMW"}]
us_list = [{"t": "STLD", "n": "Steel Dynamics"}, {"t": "WMS", "n": "Adv. Drainage"}, {"t": "NVDA", "n": "Nvidia"}, {"t": "AAPL", "n": "Apple"}, {"t": "MSFT", "n": "Microsoft"}, {"t": "GOOGL", "n": "Google"}, {"t": "AMZN", "n": "Amazon"}]

def build_table(stocks):
    rows = []
    for s in stocks:
        d = fetch_live_metrics(s['t'])
        if d: rows.append({"Trend": d['Trend'], "Wetter": d['Icon'], "Name": s['n'], "Live": d['Preis'], "Pos%": f"{d['Pos']:.1f}%", "RSI": f"{d['RSI']:.1f}"})
    st.table(pd.DataFrame(rows))

c1, c2 = st.columns(2)
with c1: st.subheader("Europa"); build_table(eu_list)
with c2: st.subheader("USA"); build_table(us_list)
