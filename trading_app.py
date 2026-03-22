import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. VOLLSTÄNDIGES TICKER-MAPPING ---
TICKER_NAMES = {
    # WETTER (Indizes & Forex)
    "EURUSD=X": "💱 EUR/USD", "EURRUB=X": "💱 EUR/RUB", 
    "^GDAXI": "📊 DAX 40", "^NDX": "📊 NASDAQ 100",
    "^STOXX50E": "📊 EuroStoxx 50", "^NSEI": "📊 Nifty 50", "XU100.IS": "📊 BIST 100",
    
    # DAX 40 KOMPLETT (🇩🇪)
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
    
    # NASDAQ 100 AUSWAHL (🇺🇸 - Die Wichtigsten)
    "AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", "AMZN": "🇺🇸 Amazon", "NVDA": "🇺🇸 Nvidia", "GOOGL": "🇺🇸 Alphabet", 
    "META": "🇺🇸 Meta", "TSLA": "🇺🇸 Tesla", "AVGO": "🇺🇸 Broadcom", "PEP": "🇺🇸 PepsiCo", "COST": "🇺🇸 Costco", 
    "ADBE": "🇺🇸 Adobe", "CSCO": "🇺🇸 Cisco", "NFLX": "🇺🇸 Netflix", "AMD": "🇺🇸 AMD", "PLTR": "🇺🇸 Palantir", 
    "MSTR": "🇺🇸 MicroStrategy", "QCOM": "🇺🇸 Qualcomm", "TXN": "🇺🇸 Texas Instruments", "INTC": "🇺🇸 Intel"
}

# FILTER: Nur Aktien (Kein ^ für Index, kein =X für Forex, kein .IS für BIST Index)
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
    chg = ((cp / float(df['Close'].iloc[-2])) - 1) * 100
    if chg > 0.15: return cp, chg, "☀️", "#00FFA3", "🟢"
    if chg < -0.15: return cp, chg, "⛈️", "#1E90FF", "🔵"
    return cp, chg, "☁️", "#8892b0", "⚪"

# --- 5. DASHBOARD ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# Update Info
now = datetime.now().strftime('%H:%M:%S')
st.markdown(f'<div class="update-info">🕒 Letztes Update: <b>{now}</b> | Intervall: <b>60s</b> | Quelle: <b>Yahoo Finance</b></div>', unsafe_allow_html=True)

# 5a. MARKT-WETTER (3 ZEILEN)
WEATHER_ROWS = [["EURUSD=X", "EURRUB=X"], ["^GDAXI", "^NDX"], ["^STOXX50E", "^NSEI", "XU100.IS"]]
for row in WEATHER_ROWS:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        df_m = get_data(t, period="5d")
        cp, chg, icon, color, dot = get_weather_info(df_m)
        prec = ".4f" if "=X" in t else ".2f"
        with cols[i]:
            st.markdown(f'<div class="weather-card" style="border-color:{color};"><small>{TICKER_NAMES.get(t,t)}</small><span> {icon}</span><br><b style="font-size:1.5rem;">{cp: ,{prec}}</b><br><span style="color:{color};">{chg:+.2f}%</span> {dot}</div>', unsafe_allow_html=True)

st.divider()

# 5b. TOP 5 AKTIEN NACH CHANCE
st.subheader("📊 Top 5 Aktien-Chancen")
signals = []
with st.spinner("Analysiere DAX & NASDAQ..."):
    for s in STOCKS_ONLY:
        df_s = get_data(s, period="10d", interval="1h")
        if not df_s.empty:
            rets = np.log(df_s['Close'] / df_s['Close'].shift(1)).dropna()
            chance = int((np.random.normal(rets.mean(), rets.std(), 1000) > 0).sum() / 10)
            cp, chg, _, _, dot = get_weather_info(df_s)
            signals.append({'Status': dot, 'Aktie': TICKER_NAMES.get(s,s), 'Trend_Val': chg, 'Trend': f"{chg:+.2f}%", 'Chance': chance})

df_sig = pd.DataFrame(signals)
if not df_sig.empty:
    c_t1, c_t2 = st.columns(2)
    with c_t1:
        st.markdown("<h4 style='color:#00FFA3;'>Top 5 CALL (Chance)</h4>", unsafe_allow_html=True)
        st.table(df_sig[df_sig['Trend_Val'] > 0].nlargest(5, 'Chance')[['Status', 'Aktie', 'Trend', 'Chance']])
    with c_t2:
        st.markdown("<h4 style='color:#1E90FF;'>Top 5 PUT (Chance)</h4>", unsafe_allow_html=True)
        st.table(df_sig[df_sig['Trend_Val'] < 0].nsmallest(5, 'Chance')[['Status', 'Aktie', 'Trend', 'Chance']])

st.divider()

# 5c. DETAIL-ANALYSE (STRIKT NUR AKTIEN)
st.subheader("🔍 Detail-Analyse (Aktien)")
# Alphabetische Sortierung für die Suche
sorted_stocks = sorted(STOCKS_ONLY, key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = st.selectbox("Aktie wählen (Währungen/Indizes ausgeblendet):", sorted_stocks, format_func=lambda x: TICKER_NAMES.get(x, x))

d_det = get_data(sel_stock, period="60d", interval="4h")
if not d_det.empty:
    cp, chg, icon, color, dot = get_weather_info(d_det)
    atr = (d_det['High'] - d_det['Low']).rolling(14).mean().iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("KURS", f"{cp:,.2f}", f"{chg:+.2f}%")
    col2.metric("CHANCE", f"{(np.random.normal(0, 1, 100) > 0).sum()}%") # Beispiel Chance
    col3.metric("ATR (14h)", f"{atr:.2f}")
    col4.metric("VOLUMEN", f"{d_det['Volume'].iloc[-1]:,.0f}")
    
    st.write("**Volumen-Verlauf (Letzte 20 Tage):**")
    st.bar_chart(d_det['Volume'].tail(40))
