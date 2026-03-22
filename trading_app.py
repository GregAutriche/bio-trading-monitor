import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. VOLLSTÄNDIGES NAMENS-MAPPING (Währungen, Indizes & Aktien) ---
TICKER_NAMES = {
    # Währungen & Indizes
    "EURUSD=X": "💱 EUR/USD", "EURRUB=X": "💱 EUR/RUB", 
    "^GDAXI": "📊 DAX 40 Index", "^NDX": "📊 NASDAQ 100 Index",
    "^STOXX50E": "📊 EuroStoxx 50", "XU100.IS": "📊 BIST 100", "^NSEI": "📊 Nifty 50",
    # Aktien DAX
    "ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF", "BAYN.DE": "🇩🇪 Bayer", 
    "BMW.DE": "🇩🇪 BMW", "DBK.DE": "🇩🇪 Deutsche Bank", "DTE.DE": "🇩🇪 Telekom", "RHM.DE": "🇩🇪 Rheinmetall", "SAP.DE": "🇩🇪 SAP",
    # Aktien US
    "AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", "NVDA": "🇺🇸 Nvidia", "TSLA": "🇺🇸 Tesla", "AMD": "🇺🇸 AMD"
}

# Gruppen für die Logik
ALL_TICKERS = list(TICKER_NAMES.keys())

# --- 3. DESIGN (MAXIMALER KONTRAST FÜR LESBARKEIT) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; }
    
    /* TABELLEN-KOPFZEILE (Extrem hell & fett) */
    thead tr th { 
        background-color: #2D3748 !important; 
        color: #FFFFFF !important; 
        font-weight: 900 !important; 
        font-size: 1.1rem !important;
        border-bottom: 3px solid #1E90FF !important;
        text-transform: uppercase !important;
    }
    
    /* TABELLEN-ZELLEN */
    tbody tr td { 
        color: #FFFFFF !important; 
        background-color: #161B22 !important;
        font-size: 1rem !important;
        border-bottom: 1px solid #30363D !important;
    }

    .stTable { border: 1px solid #4A5568 !important; border-radius: 10px !important; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] { color: #A0AEC0 !important; }
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

def get_market_signals(tickers):
    results = []
    for t in tickers:
        df = get_data(t)
        if not df.empty and len(df) > 5:
            cp = extract_val(df, 'Close', -1)
            prev = extract_val(df, 'Close', -2)
            ret = ((cp / prev) - 1) * 100
            
            # Simulation für "Chance"
            log_ret = np.log(df['Close'] / df['Close'].shift(1)).dropna()
            std = log_ret.std()
            sim = np.random.normal(0, std, 1000)
            chance_up = (sim > 0).sum() / 10 
            
            results.append({
                'Status': '🟢' if ret > 0 else '🔵', 
                'Aktie/Symbol': TICKER_NAMES.get(t, t), 
                'Trend': ret, 
                'Chance': f"{int(chance_up)}%"
            })
    df_res = pd.DataFrame(results)
    if df_res.empty: return pd.DataFrame(), pd.DataFrame()
    return df_res.nlargest(8, 'Trend'), df_res.nsmallest(8, 'Trend')

# --- 5. DASHBOARD ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5a. Top Mover (JETZT INKLUSIVE WÄHRUNGEN & INDIZES)
st.subheader("📊 Top Markt-Chancen (Alle Märkte)")
with st.spinner("Analysiere Währungen, Indizes & Aktien..."):
    calls, puts = get_market_signals(ALL_TICKERS)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("<h4 style='color:#00FFA3;'>Trend-Favoriten (Call)</h4>", unsafe_allow_html=True)
    if not calls.empty:
        st.table(calls[['Status', 'Aktie/Symbol', 'Trend', 'Chance']].reset_index(drop=True))
with col_b:
    st.markdown("<h4 style='color:#1E90FF;'>Trend-Favoriten (Put)</h4>", unsafe_allow_html=True)
    if not puts.empty:
        st.table(puts[['Status', 'Aktie/Symbol', 'Trend', 'Chance']].reset_index(drop=True))

st.divider()

# 5b. Einzelwert & Volumen
st.subheader("🔍 Detail-Analyse & Volumen-Check")
sel_stock = st.selectbox("Symbol wählen:", ALL_TICKERS, format_func=lambda x: TICKER_NAMES.get(x, x))
d_s = get_data(sel_stock, period="60d", interval="4h")

if not d_s.empty:
    has_vol = 'Volume' in d_s.columns and d_s['Volume'].tail(20).sum() > 0
    
    if has_vol:
        v_col1, v_col2 = st.columns([1, 2])
        cur_vol = extract_val(d_s, 'Volume', -1)
        avg_vol = d_s['Volume'].tail(120).mean()
        v_diff = ((cur_vol / avg_vol) - 1) * 100 if avg_vol > 0 else 0
        
        with v_col1:
            st.metric("Aktuelles Volumen", f"{cur_vol:,.0f}", f"{v_diff:+.1f}%")
            st.write(f"**Schnitt (20 Tage):** {avg_vol:,.0f}")
        with v_col2:
            st.bar_chart(d_s['Volume'].tail(40))
    else:
        st.info(f"ℹ️ Für {TICKER_NAMES.get(sel_stock)} (Währung/Index) sind keine Volumendaten verfügbar.")
        st.metric("Aktueller Kurs", f"{extract_val(d_s, 'Close', -1):,.4f}")

st.info(f"🕒 Update: {pd.Timestamp.now().strftime('%H:%M:%S')} | Alle Märkte integriert | Design-Kontrast verstärkt.")
