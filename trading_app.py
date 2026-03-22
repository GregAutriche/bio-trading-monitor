import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION & THEME ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. VOLLSTÄNDIGES NAMENS-MAPPING MIT FLAGGEN ---
TICKER_NAMES = {
    # Währungen & Indizes (Wetter-Sektion)
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", 
    "^GDAXI": "DAX 40 Index", "^NDX": "NASDAQ 100 Index",
    "^STOXX50E": "EuroStoxx 50", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    
    # DAX 40 Aktien (DE)
    "ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF", "BAYN.DE": "🇩🇪 Bayer", 
    "BEI.DE": "🇩🇪 Beiersdorf", "BMW.DE": "🇩🇪 BMW", "BNR.DE": "🇩🇪 Brenntag", "CBK.DE": "🇩🇪 Commerzbank", "CON.DE": "🇩🇪 Continental", 
    "1COV.DE": "🇩🇪 Covestro", "DTG.DE": "🇩🇪 Daimler Truck", "DBK.DE": "🇩🇪 Deutsche Bank", "DB1.DE": "🇩🇪 Deutsche Börse", 
    "DHL.DE": "🇩🇪 DHL Group", "DTE.DE": "🇩🇪 Deutsche Telekom", "EOAN.DE": "🇩🇪 E.ON", "FRE.DE": "🇩🇪 Fresenius", 
    "FME.DE": "🇩🇪 Fresenius Medical Care", "MTX.DE": "🇩🇪 MTU Aero Engines", "HEI.DE": "🇩🇪 Heidelberg Materials", 
    "HEN3.DE": "🇩🇪 Henkel", "IFX.DE": "🇩🇪 Infineon", "MBG.DE": "🇩🇪 Mercedes-Benz", "MRK.DE": "🇩🇪 Merck", 
    "MUV2.DE": "🇩🇪 Münchener Rück", "PAH3.DE": "🇩🇪 Porsche SE", "PUM.DE": "🇩🇪 Puma", "QIA.DE": "🇩🇪 Qiagen", 
    "RHM.DE": "🇩🇪 Rheinmetall", "RWE.DE": "🇩🇪 RWE", "SAP.DE": "🇩🇪 SAP", "SRT3.DE": "🇩🇪 Sartorius", "SIE.DE": "🇩🇪 Siemens", 
    "ENR.DE": "🇩🇪 Siemens Energy", "SHL.DE": "🇩🇪 Siemens Healthineers", "SY1.DE": "🇩🇪 Symrise", "TKA.DE": "🇩🇪 Thyssenkrupp", 
    "VOW3.DE": "🇩🇪 Volkswagen", "VNA.DE": "🇩🇪 Vonovia",
    
    # NASDAQ 100 Aktien (US)
    "AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", "AMZN": "🇺🇸 Amazon", "NVDA": "🇺🇸 Nvidia", "GOOGL": "🇺🇸 Alphabet (A)", 
    "META": "🇺🇸 Meta (Facebook)", "TSLA": "🇺🇸 Tesla", "AVGO": "🇺🇸 Broadcom", "PEP": "🇺🇸 PepsiCo", "COST": "🇺🇸 Costco", 
    "ADBE": "🇺🇸 Adobe", "CSCO": "🇺🇸 Cisco", "NFLX": "🇺🇸 Netflix", "AMD": "🇺🇸 AMD", "PLTR": "🇺🇸 Palantir", 
    "MSTR": "🇺🇸 MicroStrategy", "QCOM": "🇺🇸 Qualcomm", "TXN": "🇺🇸 Texas Instruments", "ISRG": "🇺🇸 Intuitive Surgical", "PANW": "🇺🇸 Palo Alto"
}

# Listen-Definitionen
WEATHER_STRUCTURE = [["EURUSD=X", "EURRUB=X"], ["^GDAXI", "^NDX"], ["^STOXX50E", "XU100.IS", "^NSEI"]]
STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k and not ".IS" in k]

# --- 3. DESIGN (DARK BIO-TRADING) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .weather-card { text-align:center; padding:12px; border-radius:10px; background:rgba(30,144,255,0.05); border: 1px solid #1E90FF; margin-bottom: 10px; }
    table { background-color: #161B22 !important; color: white !important; border-radius: 10px; width: 100%; }
    thead tr th { background-color: #1F2937 !important; color: #8892b0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="5d", interval="1h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def extract_val(df, column, idx):
    try:
        val = df[column].iloc[idx]
        return float(val.iloc) if hasattr(val, 'iloc') else float(val)
    except: return 0.0

def get_top_5_signals(tickers):
    signals = []
    for t in tickers:
        df = get_data(t)
        if not df.empty and len(df) > 1:
            cp = extract_val(df, 'Close', -1)
            prev = extract_val(df, 'Close', -2)
            ret = ((cp / prev) - 1) * 100 if prev > 0 else 0
            signals.append({'Aktie': TICKER_NAMES.get(t, t), 'Preis': cp, 'Trend': ret})
    
    df_sig = pd.DataFrame(signals)
    if df_sig.empty: return pd.DataFrame(), pd.DataFrame()
    return df_sig.nlargest(5, 'Trend'), df_sig.nsmallest(5, 'Trend')

# --- 5. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5a. MARKT-WETTER
st.subheader("🌐 Globales Markt-Wetter")
for row in WEATHER_STRUCTURE:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        w_data = get_data(t)
        if not w_data.empty:
            cp_w = extract_val(w_data, 'Close', -1)
            chg_w = ((cp_w / extract_val(w_data, 'Close', -2)) - 1) * 100
            prec = 5 if "=X" in t else 2
            color = "#00FFA3" if chg_w > 0.1 else "#FF4B4B" if chg_w < -0.1 else "#FFD700"
            with cols[i]:
                st.markdown(f'<div class="weather-card" style="border-color:{color};">'
                            f'<small style="color:#8892b0;">{TICKER_NAMES.get(t, t)}</small><br>'
                            f'<b style="font-size:1.3rem; color:white;">{cp_w:,.{prec}f}</b><br>'
                            f'<span style="color:{color}; font-size:0.9rem;">{chg_w:+.2f}%</span></div>', unsafe_allow_html=True)

st.divider()

# 5b. TOP 5 TABELLEN (NUR AKTIEN MIT FLAGGEN)
st.subheader("📊 Top 5 Aktien-Bewegungen (Aktien only)")
t_col1, t_col2 = st.columns(2)

with st.spinner("Aktualisiere Top-Werte..."):
    calls, puts = get_top_5_signals(STOCKS_ONLY)

if not calls.empty:
    with t_col1:
        st.markdown("<h4 style='color:#00FFA3;'>🟢 Top 5 CALL (Long-Fokus)</h4>", unsafe_allow_html=True)
        st.table(calls[['Aktie', 'Preis', 'Trend']].style.format({'Preis': '{:.2f}', 'Trend': '{:+.2f}%'}))

    with t_col2:
        st.markdown("<h4 style='color:#FF4B4B;'>🔴 Top 5 PUT (Short-Fokus)</h4>", unsafe_allow_html=True)
        st.table(puts[['Aktie', 'Preis', 'Trend']].style.format({'Preis': '{:.2f}', 'Trend': '{:+.2f}%'}))

st.divider()

# 5c. EINZELWERT ANALYSE (DEIN WUNSCH: FLAGGE IN DER BOX)
st.subheader("🔍 Einzelwert im Detail analysieren")
all_stocks_sorted = sorted(STOCKS_ONLY, key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = st.selectbox("Wähle einen Wert:", all_stocks_sorted, format_func=lambda x: TICKER_NAMES.get(x, x))

d_s = get_data(sel_stock, period="60d", interval="4h")
if not d_s.empty:
    cp = extract_val(d_s, 'Close', -1)
    st.metric(f"Aktueller Kurs: {TICKER_NAMES[sel_stock]}", f"{cp:,.2f}")
    st.line_chart(d_s['Close'])

st.info(f"🕒 Letztes Update: {pd.Timestamp.now().strftime('%H:%M:%S')} | Quelle: Yahoo Finance")
