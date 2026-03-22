import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", 
    "^GDAXI": "DAX 40", "^NDX": "NASDAQ 100",
    "^STOXX50E": "EuroStoxx 50", "^NSEI": "Nifty 50", "XU100.IS": "BIST 100",
    "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF", 
    "BAYN.DE": "Bayer", "BMW.DE": "BMW", "DBK.DE": "Deutsche Bank", "DTE.DE": "Telekom", 
    "RHM.DE": "Rheinmetall", "SAP.DE": "SAP", "AAPL": "Apple", "MSFT": "Microsoft", 
    "NVDA": "Nvidia", "TSLA": "Tesla", "AMD": "AMD", "PLTR": "Palantir"
}
STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k]

# --- 3. DESIGN (MAXIMALER KONTRAST & DARK MODE) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; }
    .weather-card { 
        text-align:center; border-radius:12px; background:rgba(255,255,255,0.03); 
        border: 2px solid #333; padding: 15px; margin-bottom: 10px; 
    }
    thead tr th { background-color: #2D3748 !important; color: #FFFFFF !important; font-weight: 900 !important; border-bottom: 3px solid #1E90FF !important; }
    tbody tr td { color: #FFFFFF !important; background-color: #161B22 !important; border-bottom: 1px solid #30363D !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="1h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def get_weather_info(df):
    if df.empty or len(df) < 2: return 0.0, 0.0, "☁️", "#8892b0", "⚪"
    cp = float(df['Close'].iloc[-1])
    prev = float(df['Close'].iloc[-2])
    chg = ((cp / prev) - 1) * 100
    
    # Wetter- & Action-Logik
    if chg > 0.15: return cp, chg, "☀️", "#00FFA3", "🟢"
    if chg < -0.15: return cp, chg, "⛈️", "#1E90FF", "🔵"
    return cp, chg, "☁️", "#8892b0", "⚪"

# --- 5. DASHBOARD ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5a. MARKT-WETTER (3 ZEILEN MIT VOLLER LOGIK)
st.subheader("🌐 Globales Markt-Wetter")
WEATHER_ROWS = [["EURUSD=X", "EURRUB=X"], ["^GDAXI", "^NDX"], ["^STOXX50E", "^NSEI", "XU100.IS"]]

for row in WEATHER_ROWS:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        df_m = get_data(t, period="5d")
        cp, chg, icon, color, dot = get_weather_info(df_m)
        prec = ".4f" if "=X" in t else ".2f"
        
        with cols[i]:
            st.markdown(f"""
                <div class="weather-card" style="border-color:{color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                        <small style="color:#8892b0;">{TICKER_NAMES.get(t,t)}</small>
                        <span style="font-size:1.2rem;">{icon}</span>
                    </div>
                    <b style="font-size:1.6rem; color:white;">{cp: ,{prec}}</b><br>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                        <span style="color:{color}; font-weight:bold; font-size:1.1rem;">{chg:+.2f}%</span>
                        <span style="font-size:1.3rem;">{dot}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.write("") 

st.divider()

# 5b. TOP 5 AKTIEN NACH CHANCE
# --- 5b. TOP 5 AKTIEN NACH CHANCE (MIT TREND-FILTER) ---
st.subheader("📊 Top 5 Aktien-Chancen")
signals = []
for s in STOCKS_ONLY:
    df_s = get_data(s, period="10d", interval="1h")
    if not df_s.empty:
        # Statistische Chance berechnen
        rets = np.log(df_s['Close'] / df_s['Close'].shift(1)).dropna()
        chance = int((np.random.normal(rets.mean(), rets.std(), 1000) > 0).sum() / 10)
        cp, chg, icon, color, dot = get_weather_info(df_s)
        signals.append({
            'Status': dot, 
            'Aktie': TICKER_NAMES.get(s,s), 
            'Trend_Val': chg, 
            'Trend': f"{chg:+.2f}%", 
            'Chance': chance
        })

df_sig = pd.DataFrame(signals)
c_t1, c_t2 = st.columns(2)

if not df_sig.empty:
    with c_t1:
        st.markdown("<h4 style='color:#00FFA3;'>Top 5 CALL (Chance)</h4>", unsafe_allow_html=True)
        # FILTER: Nur positiver Trend, dann nach höchster Chance sortieren
        calls = df_sig[df_sig['Trend_Val'] > 0].nlargest(5, 'Chance')
        st.table(calls[['Status', 'Aktie', 'Trend', 'Chance']])
        
    with c_t2:
        st.markdown("<h4 style='color:#1E90FF;'>Top 5 PUT (Chance)</h4>", unsafe_allow_html=True)
        # FILTER: Nur negativer Trend, dann nach niedrigster Chance sortieren
        puts = df_sig[df_sig['Trend_Val'] < 0].nsmallest(5, 'Chance')
        st.table(puts[['Status', 'Aktie', 'Trend', 'Chance']])


st.divider()

# 5c. DETAIL-ANALYSE
st.subheader("🔍 Einzelwert-Details & Volumen")
sel_stock = st.selectbox("Aktie wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])
d_det = get_data(sel_stock, period="60d", interval="4h")

if not d_det.empty:
    cp, chg, icon, color, dot = get_weather_info(d_det)
    # ATR Berechnung
    atr = (d_det['High'] - d_det['Low']).rolling(14).mean().iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("KURS", f"{cp:,.2f}", f"{chg:+.2f}%")
    col2.metric("WETTER", f"{icon} {dot}")
    col3.metric("ATR (14)", f"{atr:.2f}")
    col4.metric("VOLUMEN", f"{d_det['Volume'].iloc[-1]:,.0f}")
    
    st.bar_chart(d_det['Volume'].tail(40))
