import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. NAMENS-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40 Index", "^NDX": "NASDAQ 100 Index",
    "^STOXX50E": "EuroStoxx 50", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    "ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF", "BAYN.DE": "🇩🇪 Bayer", 
    "BMW.DE": "🇩🇪 BMW", "DBK.DE": "🇩🇪 Deutsche Bank", "DTE.DE": "🇩🇪 Telekom", "RHM.DE": "🇩🇪 Rheinmetall", "SAP.DE": "🇩🇪 SAP",
    "AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", "NVDA": "🇺🇸 Nvidia", "TSLA": "🇺🇸 Tesla", "AMD": "🇺🇸 AMD"
}
STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k]

# --- 3. DESIGN (KONTRAST-OPTIMIERT) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; color: #E0E0E0 !important; }
    
    /* Tabellen-Design für bessere Lesbarkeit */
    thead tr th { 
        background-color: #1F2937 !important; 
        color: #FFFFFF !important; /* Strahlendes Weiß für Überschriften */
        font-weight: bold !important;
        border-bottom: 2px solid #1E90FF !important;
    }
    tbody tr td { 
        color: #F0F0F0 !important; /* Helles Grau für Zelleninhalt */
        background-color: #161B22 !important;
    }
    .stTable { border-radius: 10px; overflow: hidden; border: 1px solid #30363D; }
    
    /* Wetter-Karten */
    .weather-card { text-align:center; border-radius:10px; background:rgba(30,144,255,0.05); border: 1px solid #1E90FF; margin-bottom: 10px; padding: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="10d", interval="1h"):
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

def get_market_signals(tickers):
    results = []
    for t in tickers:
        df = get_data(t)
        if not df.empty and len(df) > 5:
            cp = extract_val(df, 'Close', -1)
            ret = ((cp / extract_val(df, 'Close', -2)) - 1) * 100
            # Simulation für "Chance"
            log_ret = np.log(df['Close'] / df['Close'].shift(1)).dropna()
            prob_up = (np.random.normal(0, log_ret.std(), 100) > 0).sum() # Vereinfachte Chance
            results.append({'Status': '🟢' if ret > 0 else '🔵', 'Aktie': TICKER_NAMES.get(t, t), 'Trend': ret, 'Chance': f"{prob_up}%", 'RawChance': prob_up})
    df_res = pd.DataFrame(results)
    return df_res.nlargest(5, 'Trend'), df_res.nsmallest(5, 'Trend')

# --- 5. DASHBOARD ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# Top 5 Mover
st.subheader("📊 Top 5 Markt-Chancen")
with st.spinner("Berechne Chancen..."):
    calls, puts = get_market_signals(STOCKS_ONLY)

c1, c2 = st.columns(2)
with c1:
    st.markdown("<h4 style='color:#00FFA3;'>Trend-Favoriten (Call)</h4>", unsafe_allow_html=True)
    if not calls.empty:
        st.table(calls[['Status', 'Aktie', 'Trend', 'Chance']].style.format({'Trend': '{:+.2f}%'}))
with c2:
    st.markdown("<h4 style='color:#1E90FF;'>Trend-Favoriten (Put)</h4>", unsafe_allow_html=True)
    if not puts.empty:
        st.table(puts[['Status', 'Aktie', 'Trend', 'Chance']].style.format({'Trend': '{:+.2f}%'}))

st.divider()

# Einzelwert mit Volumen
st.subheader("🔍 Detail-Analyse & Volumen")
sel_stock = st.selectbox("Aktie wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES.get(x, x))
d_s = get_data(sel_stock, period="60d", interval="4h")

if not d_s.empty:
    v_col1, v_col2 = st.columns([1, 2])
    cur_vol = extract_val(d_s, 'Volume', -1)
    avg_vol = d_s['Volume'].tail(120).mean()
    v_diff = ((cur_vol / avg_vol) - 1) * 100 if avg_vol > 0 else 0
    
    with v_col1:
        st.metric("Aktuelles Volumen", f"{cur_vol:,.0f}", f"{v_diff:+.1f}%")
        st.write(f"**Durchschnitt (20 Tage):** {avg_vol:,.0f}")
    with v_col2:
        st.bar_chart(d_s['Volume'].tail(40))

st.info(f"🕒 Stand: {pd.Timestamp.now().strftime('%H:%M:%S')} | Spaltenbeschriftungen wurden für besseren Kontrast aufgehellt.")
