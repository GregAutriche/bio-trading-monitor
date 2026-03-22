import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION & THEME ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. VOLLSTÄNDIGES NAMENS-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40 Index", "^NDX": "NASDAQ 100 Index",
    "^STOXX50E": "EuroStoxx 50", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    # DAX 40 (DE)
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
    # NASDAQ 100 (US)
    "AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", "AMZN": "🇺🇸 Amazon", "NVDA": "🇺🇸 Nvidia", "GOOGL": "🇺🇸 Alphabet (A)", 
    "META": "🇺🇸 Meta (Facebook)", "TSLA": "🇺🇸 Tesla", "AVGO": "🇺🇸 Broadcom", "PEP": "🇺🇸 PepsiCo", "COST": "🇺🇸 Costco", 
    "ADBE": "🇺🇸 Adobe", "CSCO": "🇺🇸 Cisco", "NFLX": "🇺🇸 Netflix", "AMD": "🇺🇸 AMD", "PLTR": "🇺🇸 Palantir", 
    "MSTR": "🇺🇸 MicroStrategy", "QCOM": "🇺🇸 Qualcomm", "TXN": "🇺🇸 Texas Instruments", "ISRG": "🇺🇸 Intuitive Surgical", "PANW": "🇺🇸 Palo Alto"
}

WEATHER_STRUCTURE = [["EURUSD=X", "EURRUB=X"], ["^GDAXI", "^NDX"], ["^STOXX50E", "XU100.IS", "^NSEI"]]
STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k and not ".IS" in k]

# --- 3. DESIGN (DARK BIO-TRADING) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .weather-card { text-align:center; border-radius:10px; background:rgba(30,144,255,0.05); border: 1px solid #1E90FF; margin-bottom: 10px; }
    .analysis-box { padding: 20px; border-radius: 12px; background: rgba(255,255,255,0.02); border: 1px solid #333; margin-top: 15px; }
    table { background-color: #161B22 !important; color: white !important; border-radius: 10px; width: 100%; border: none !important; }
    thead tr th { background-color: #1F2937 !important; color: #8892b0 !important; border: none !important; }
    td { border: none !important; padding: 10px !important; }
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

def extract_val(df, column, idx):
    try:
        val = df[column].iloc[idx]
        return float(val.iloc) if hasattr(val, 'iloc') else float(val)
    except: return 0.0

def get_action_style(change):
    if change > 0.15: return "☀️", "#00FFA3", "🟢" # Sonnig / Grün (Call)
    if change < -0.15: return "⛈️", "#1E90FF", "🔵" # Gewitter / Blau (Put)
    return "☁️", "#8892b0", "⚪" # Bewölkt / Grau (Warten)

def get_top_5_signals(tickers):
    signals = []
    for t in tickers:
        df = get_data(t, period="5d", interval="1h")
        if not df.empty and len(df) > 1:
            cp = extract_val(df, 'Close', -1)
            prev = extract_val(df, 'Close', -2)
            ret = ((cp / prev) - 1) * 100 if prev > 0 else 0
            _, _, dot = get_action_style(ret)
            signals.append({'Aktie': TICKER_NAMES.get(t, t), 'Preis': cp, 'Trend': ret, 'Aktion': dot})
    
    df_sig = pd.DataFrame(signals)
    if df_sig.empty: return pd.DataFrame(), pd.DataFrame()
    return df_sig.nlargest(5, 'Trend'), df_sig.nsmallest(5, 'Trend')

# --- 5. DASHBOARD ---
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
            icon, color, dot = get_action_style(chg_w)
            prec = 5 if "=X" in t else 2
            with cols[i]:
                st.markdown(f"""
                    <div class="weather-card" style="border-color:{color}; padding: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                            <small style="color:#8892b0;">{TICKER_NAMES.get(t, t)}</small>
                            <span style="font-size:1.2rem;">{icon}</span>
                        </div>
                        <b style="font-size:1.5rem; color:white;">{cp_w:,.{prec}f}</b><br>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px;">
                            <span style="color:{color}; font-weight:bold; font-size:1.1rem;">{chg_w:+.2f}%</span>
                            <span style="color:{color}; font-size:1.3rem;">{dot}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

st.divider()

# 5b. TOP 5 TABELLEN (MIT AKTIONS-LOGIK)
st.subheader("📊 Top 5 Aktien-Bewegungen")
t_col1, t_col2 = st.columns(2)
with st.spinner("Aktualisiere Top-Werte..."):
    calls, puts = get_top_5_signals(STOCKS_ONLY)

if not calls.empty:
    with t_col1:
        st.markdown("<h4 style='color:#00FFA3;'>🟢 Top 5 CALL (Mover)</h4>", unsafe_allow_html=True)
        st.table(calls[['Aktion', 'Aktie', 'Preis', 'Trend']].style.format({'Preis': '{:.2f}', 'Trend': '{:+.2f}%'}))
    with t_col2:
        st.markdown("<h4 style='color:#1E90FF;'>🔵 Top 5 PUT (Mover)</h4>", unsafe_allow_html=True)
        st.table(puts[['Aktion', 'Aktie', 'Preis', 'Trend']].style.format({'Preis': '{:.2f}', 'Trend': '{:+.2f}%'}))

st.divider()

# 5c. EINZELWERT ANALYSE
st.subheader("🔍 Einzelwert im Detail analysieren")
all_stocks_sorted = sorted(STOCKS_ONLY, key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = st.selectbox("Aktie wählen:", all_stocks_sorted, format_func=lambda x: TICKER_NAMES.get(x, x))

d_s = get_data(sel_stock, period="60d", interval="1h")

if not d_s.empty:
    cp = extract_val(d_s, 'Close', -1)
    chg = ((cp / extract_val(d_s, 'Close', -2)) - 1) * 100
    cur_vol = extract_val(d_s, 'Volume', -1)
    avg_vol = d_s['Volume'].tail(20).mean()
    vol_ratio = (cur_vol / avg_vol) if avg_vol > 0 else 1
    
    # Aktions-Check
    icon, color, dot = get_action_style(chg)
    status_text = "KAUFEN" if dot == "🟢" else "VERKAUFEN" if dot == "🔵" else "WARTEN"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Kurs", f"{cp:,.2f}", f"{chg:+.2f}%")
    m2.metric("Wetter", icon)
    m3.metric("Volumen", f"{vol_ratio:.2f}x")
    m4.markdown(f'<div style="text-align:center; background:{color}22; padding:10px; border-radius:8px; border:1px solid {color}; color:{color}; font-weight:bold;"><small>STATUS</small><br>{dot} {status_text}</div>', unsafe_allow_html=True)

    # KOMBI-CHART
    fig, ax1 = plt.subplots(figsize=(12, 5), facecolor='#0E1117')
    ax1.set_facecolor('#0E1117')
    ax1.plot(d_s.index, d_s['Close'], color='#1E90FF', linewidth=2)
    ax1.tick_params(axis='y', labelcolor='#E0E0E0')
    
    ax2 = ax1.twinx()
    # Volumensfarben: Grün bei Kursplus, Blau bei Kursminus (passend zur Aktionslogik)
    v_cols = ['#00FFA3' if d_s['Close'].iloc[i] >= d_s['Open'].iloc[i] else '#1E90FF' for i in range(len(d_s))]
    ax2.bar(d_s.index, d_s['Volume'], color=v_cols, alpha=0.3, width=0.03)
    ax2.set_ylim(0, d_s['Volume'].max() * 4)
    
    st.pyplot(fig)

st.info(f"🕒 Stand: {pd.Timestamp.now().strftime('%H:%M:%S')} | Quelle: Yahoo Finance")
