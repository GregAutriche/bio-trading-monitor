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
    .weather-card { text-align:center; padding:12px; border-radius:10px; background:rgba(30,144,255,0.05); border: 1px solid #1E90FF; margin-bottom: 10px; }
    .analysis-box { padding: 20px; border-radius: 12px; background: rgba(255,255,255,0.02); border: 1px solid #333; margin-top: 15px; }
    table { background-color: #161B22 !important; color: white !important; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="4h"):
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

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_cp = np.abs(df['High'] - df['Close'].shift())
    low_cp = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    return tr.rolling(period).mean().iloc[-1]

# --- 5. DASHBOARD ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5a. MARKT-WETTER
for row in WEATHER_STRUCTURE:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        w_data = get_data(t)
        if not w_data.empty:
            cp_w = extract_val(w_data, 'Close', -1)
            chg_w = ((cp_w / extract_val(w_data, 'Close', -2)) - 1) * 100
            color = "#00FFA3" if chg_w > 0.1 else "#FF4B4B" if chg_w < -0.1 else "#FFD700"
            prec = 5 if "=X" in t else 2
            with cols[i]:
                st.markdown(f'<div class="weather-card" style="border-color:{color};"><small style="color:#8892b0;">{TICKER_NAMES.get(t, t)}</small><br><b style="font-size:1.2rem;">{cp_w:,.{prec}f}</b><br><span style="color:{color};">{chg_w:+.2f}%</span></div>', unsafe_allow_html=True)

st.divider()

# 5b. EINZELWERT ANALYSE
st.subheader("🔍 Einzelwert im Detail analysieren")
all_stocks_sorted = sorted(STOCKS_ONLY, key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = st.selectbox("Aktie wählen:", all_stocks_sorted, format_func=lambda x: TICKER_NAMES.get(x, x))

d_s = get_data(sel_stock, period="60d", interval="4h")

if not d_s.empty:
    cp = extract_val(d_s, 'Close', -1)
    prev_cp = extract_val(d_s, 'Close', -2)
    change = ((cp / prev_cp) - 1) * 100
    
    # ATR & Volumen
    atr = calculate_atr(d_s)
    cur_vol = extract_val(d_s, 'Volume', -1)
    avg_vol = d_s['Volume'].tail(20).mean()
    vol_ratio = (cur_vol / avg_vol) if avg_vol > 0 else 1
    
    # Strategie-Logik
    # CALL: Preis > EMA20 (simuliert) + hohes Volumen
    # PUT: Preis < EMA20 (simuliert) + hohes Volumen
    # WARTEN: Wenig Volumen oder Seitwärts
    if vol_ratio > 1.2 and change > 0.5: recommendation, rec_col = "CALL (KAUFEN)", "#00FFA3"
    elif vol_ratio > 1.2 and change < -0.5: recommendation, rec_col = "PUT (VERKAUFEN)", "#FF4B4B"
    else: recommendation, rec_col = "ABWARTEN / NEUTRAL", "#FFD700"

    # Anzeige Metriken
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Kurs", f"{cp:,.2f}", f"{change:+.2f}%")
    m2.metric("ATR (14)", f"{atr:,.2f}")
    m3.metric("Volumen-Trend", f"{vol_ratio:.2f}x", f"{'Hoch' if vol_ratio > 1 else 'Niedrig'}")
    m4.markdown(f'<div style="text-align:center; background:{rec_col}22; padding:10px; border-radius:8px; border:1px solid {rec_col}; color:{rec_col}; font-weight:bold;"><small>EMPFEHLUNG</small><br>{recommendation}</div>', unsafe_allow_html=True)

    st.line_chart(d_s['Close'])

    # Detail-Box
    st.markdown(f"""
    <div class="analysis-box">
        <h4>📊 Analyse-Zusammenfassung: {TICKER_NAMES[sel_stock]}</h4>
        <p>Der aktuelle Trend wird als <b>{recommendation}</b> eingestuft. 
        Die <b>ATR</b> von {atr:.2f} deutet auf eine {'erhöhte' if atr > (cp*0.02) else 'normale'} Volatilität hin. 
        Das Volumen liegt aktuell bei <b>{vol_ratio:.1f}-fachen</b> des Durchschnitts, was den Trend {'bestätigt' if vol_ratio > 1.2 else 'noch nicht ausreichend untermauert'}.</p>
    </div>
    """, unsafe_allow_html=True)

st.info(f"🕒 Stand: {pd.Timestamp.now().strftime('%H:%M:%S')} | Quelle: Yahoo Finance")
