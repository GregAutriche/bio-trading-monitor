import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING (Muss VOR dem Wetter-Block stehen!) ---
TICKER_NAMES = {
    "EURUSD=X": "💱 EUR/USD", "EURRUB=X": "💱 EUR/RUB", 
    "^GDAXI": "📊 DAX 40", "^NDX": "📊 NASDAQ 100",
    "^STOXX50E": "📊 EuroStoxx 50", "^NSEI": "📊 Nifty 50", "XU100.IS": "📊 BIST 100",
    "ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF", 
    "BAYN.DE": "🇩🇪 Bayer", "BMW.DE": "🇩🇪 BMW", "DBK.DE": "🇩🇪 Deutsche Bank", "DTE.DE": "🇩🇪 Telekom", 
    "RHM.DE": "🇩🇪 Rheinmetall", "SAP.DE": "🇩🇪 SAP", "AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", 
    "NVDA": "🇺🇸 Nvidia", "TSLA": "🇺🇸 Tesla", "AMD": "🇺🇸 AMD", "PLTR": "🇺🇸 Palantir"
}

# --- 3. DESIGN (MAXIMALER KONTRAST FÜR LESBARKEIT) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; }
    .weather-card { text-align:center; border-radius:10px; background:rgba(30,144,255,0.08); border: 1px solid #1E90FF; margin-bottom: 10px; padding: 15px; }
    thead tr th { background-color: #2D3748 !important; color: #FFFFFF !important; font-weight: 900 !important; font-size: 1.1rem !important; border-bottom: 3px solid #1E90FF !important; text-transform: uppercase !important; }
    tbody tr td { color: #FFFFFF !important; background-color: #161B22 !important; border-bottom: 1px solid #30363D !important; }
    .stTable { border: 1px solid #4A5568 !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="15d", interval="1h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def extract_val(df, column, idx):
    try:
        val = df[column].iloc[idx]
        return float(val)
    except: return 0.0

# --- 5. DASHBOARD ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5a. MARKT-WETTER (STRUKTURIERT IN 3 ZEILEN)
st.subheader("🌐 Globales Markt-Wetter")
WEATHER_ROWS = [
    ["EURUSD=X", "EURRUB=X"],                   # 1. Zeile: Währungen
    ["^GDAXI", "^NDX"],                         # 2. Zeile: DAX, NASDAQ
    ["^STOXX50E", "^NSEI", "XU100.IS"]          # 3. Zeile: EuroStoxx, NIFTY, BIST
]

for row in WEATHER_ROWS:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        df_m = get_data(t)
        if not df_m.empty:
            cp_m = extract_val(df_m, 'Close', -1)
            chg_m = ((cp_m / extract_val(df_m, 'Close', -2)) - 1) * 100
            color = "#00FFA3" if chg_m > 0 else "#1E90FF"
            
            # Formatierung (Währungen 4 Stellen, Indizes 2 Stellen)
            prec = ".4f" if "=X" in t else ".2f"
            price_str = f"{cp_m: ,{prec}}"
            
            with cols[i]:
                st.markdown(f"""
                    <div class="weather-card" style="border-color:{color};">
                        <small style="color:#A0AEC0;">{TICKER_NAMES.get(t, t)}</small><br>
                        <b style="font-size:1.4rem;">{price_str}</b><br>
                        <span style="color:{color}; font-weight:bold;">{chg_m:+.2f}%</span>
                    </div>
                """, unsafe_allow_html=True)
    st.write("") # Abstand

st.divider()

# 5b. EINZELWERT ANALYSE & VOLUMEN (20 TAGE)
st.subheader("🔍 Detail-Analyse & Volumen-Trend")
sel_stock = st.selectbox("Symbol wählen:", list(TICKER_NAMES.keys()), format_func=lambda x: TICKER_NAMES[x])

d_s = get_data(sel_stock, period="60d", interval="4h")
if not d_s.empty:
    has_vol = 'Volume' in d_s.columns and d_s['Volume'].tail(10).sum() > 0
    v1, v2 = st.columns([1, 2])
    if has_vol:
        cur_v = extract_val(d_s, 'Volume', -1)
        avg_v = d_s['Volume'].tail(120).mean() # 20 Tage Schnitt
        v_diff = ((cur_v / avg_v) - 1) * 100 if avg_v > 0 else 0
        v1.metric("Aktuelles Volumen", f"{cur_v:,.0f}", f"{v_diff:+.1f}%")
        v2.bar_chart(d_s['Volume'].tail(40))
    else:
        st.info("Keine Volumendaten für dieses Symbol verfügbar.")
