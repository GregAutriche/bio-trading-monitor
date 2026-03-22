import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "💱 EUR/USD", "EURRUB=X": "💱 EUR/RUB", 
    "^GDAXI": "📊 DAX 40", "^NDX": "📊 NASDAQ 100",
    "^STOXX50E": "📊 EuroStoxx 50", "^NSEI": "📊 Nifty 50", "XU100.IS": "📊 BIST 100",
    "ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF", "BAYN.DE": "🇩🇪 Bayer", 
    "BMW.DE": "🇩🇪 BMW", "DBK.DE": "🇩🇪 Deutsche Bank", "DTE.DE": "🇩🇪 Telekom", "RHM.DE": "🇩🇪 Rheinmetall", 
    "RWE.DE": "🇩🇪 RWE", "SAP.DE": "🇩🇪 SAP", "AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", 
    "NVDA": "🇺🇸 Nvidia", "TSLA": "🇺🇸 Tesla", "AMD": "🇺🇸 AMD", "PLTR": "🇺🇸 Palantir"
}
STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k and k != "XU100.IS"]

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; }
    .weather-card { text-align:center; border-radius:12px; background:rgba(255,255,255,0.03); border: 2px solid #333; padding: 15px; margin-bottom: 10px; }
    .update-info { color: #8892b0; font-size: 0.85rem; margin-bottom: 20px; text-align: center; border: 1px solid #1E90FF; padding: 5px; border-radius: 5px; }
    thead tr th { background-color: #2D3748 !important; color: #FFFFFF !important; font-weight: 900 !important; border-bottom: 3px solid #1E90FF !important; }
    tbody tr td { color: #FFFFFF !important; background-color: #161B22 !important; border-bottom: 1px solid #30363D !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ZENTRALE FUNKTION ---
@st.cache_data(ttl=60)
def get_analysis(ticker):
    try:
        df = yf.download(ticker, period="30d", interval="1h", progress=False)
        if df.empty or len(df) < 15: return {"cp": 0.0, "chg": 0.0, "chance": 50, "atr": 0.0, "vol": 0, "df": df}
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        cp = float(df['Close'].iloc[-1])
        chg = ((cp / float(df['Close'].iloc[-2])) - 1) * 100
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        np.random.seed(42)
        sim = np.random.normal(np.log(df['Close']/df['Close'].shift(1)).dropna().mean(), 0.01, 1000)
        chance = int((sim > 0).sum() / 10)
        return {"cp": cp, "chg": chg, "chance": chance, "atr": atr, "vol": int(df['Volume'].iloc[-1]), "df": df}
    except: return {"cp": 0.0, "chg": 0.0, "chance": 50, "atr": 0.0, "vol": 0, "df": pd.DataFrame()}

def get_style(chg):
    if chg > 0.15: return "☀️", "#00FFA3", "🟢"
    if chg < -0.15: return "⛈️", "#1E90FF", "🔵"
    return "☁️", "#8892b0", "⚪"

# --- 5. DASHBOARD ---
st.title("🚀 Bio-Trading Monitor Live PRO")
st.markdown(f'<div class="update-info">🕒 Update: <b>{datetime.now().strftime("%H:%M:%S")}</b> | Intervall: <b>60s</b></div>', unsafe_allow_html=True)

# 5a. MARKT-WETTER (3 ZEILEN)
WEATHER_ROWS = [["EURUSD=X", "EURRUB=X"], ["^GDAXI", "^NDX"], ["^STOXX50E", "^NSEI", "XU100.IS"]]
for row in WEATHER_ROWS:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        res = get_analysis(t)
        icon, color, dot = get_style(res["chg"])
        with cols[i]:
            st.markdown(f'<div class="weather-card" style="border-color:{color};"><small>{TICKER_NAMES.get(t,t)}</small> {icon}<br><b style="font-size:1.5rem;">{res["cp"]: ,.2f if "^" in t else .4f}</b><br><span style="color:{color};">{res["chg"]:+.2f}%</span> {dot}</div>', unsafe_allow_html=True)

st.divider()

# 5b. TOP 5 AKTIEN
st.subheader("📊 Top 5 Aktien-Chancen")
signals = []
for s in STOCKS_ONLY:
    r = get_analysis(s)
    if r["cp"] > 0:
        _, _, dot = get_style(r["chg"])
        signals.append({'Status': dot, 'Aktie': TICKER_NAMES.get(s,s), 'Trend_Val': r["chg"], 'Trend': f"{r['chg']:+.2f}%", 'Chance': r["chance"]})

df_sig = pd.DataFrame(signals)
if not df_sig.empty:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4 style='color:#00FFA3;'>Top 5 CALL (Chance)</h4>", unsafe_allow_html=True)
        st.table(df_sig[df_sig['Trend_Val'] > 0].nlargest(5, 'Chance')[['Status', 'Aktie', 'Trend', 'Chance']])
    with c2:
        st.markdown("<h4 style='color:#1E90FF;'>Top 5 PUT (Chance)</h4>", unsafe_allow_html=True)
        st.table(df_sig[df_sig['Trend_Val'] < 0].nsmallest(5, 'Chance')[['Status', 'Aktie', 'Trend', 'Chance']])

st.divider()

# 5c. DETAIL-ANALYSE (FIX: REIHENFOLGE GEÄNDERT)
st.subheader("🔍 Detail-Analyse & Volumen")
# Zuerst die Selectbox erstellen, damit sel_stock definiert ist!
sorted_stocks = sorted(STOCKS_ONLY, key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = st.selectbox("Aktie wählen:", sorted_stocks, format_func=lambda x: TICKER_NAMES.get(x, x))

# Jetzt sel_stock für die Analyse nutzen
res_d = get_analysis(sel_stock)
if res_d["cp"] > 0:
    icon_d, _, dot_d = get_style(res_d["chg"])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("KURS", f"{res_d['cp']:,.2f}", f"{res_d['chg']:+.2f}%")
    col2.metric("CHANCE", f"{res_d['chance']}%", delta=f"{res_d['chance']-50}%")
    col3.metric("ATR (14h)", f"{res_d['atr']:.2f}")
    col4.metric("VOLUMEN", f"{res_d['vol']:,.0f}")

    # Volumen-Profil
    st.write(f"**Status:** {icon_d} {dot_d} | **Volumen-Profil (Letzte 40 Perioden):**")
    st.bar_chart(res_d["df"]['Volume'].tail(40), color="#1E90FF")
