import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50",
    "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer",
    "BMW.DE": "BMW", "DBK.DE": "Deutsche Bank", "DTE.DE": "Telekom", "SAP.DE": "SAP", "SIE.DE": "Siemens",
    "AAPL": "Apple", "NVDA": "Nvidia", "TSLA": "Tesla", "MSFT": "Microsoft", "AMZN": "Amazon"
}

TICKER_GROUPS = {
    "DAX 40 (DE)": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "ADS.DE", "BMW.DE", "BAYN.DE", "BAS.DE", "DBK.DE"],
    "EuroStoxx 50 (EU)": ["AIR.PA", "MC.PA", "OR.PA", "ASML.AS", "SAN.PA", "BNP.PA"],
    "NASDAQ 100 (US)": ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN"],
    "BIST 100 (TR)": ["THYAO.IS", "ASELS.IS", "KCHOL.IS"],
    "Nifty 50 (IN)": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
}

# --- 3. CSS DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; min-height: 80px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; color: white; }
    .bullish { color: #00FFA3; font-weight: bold; }
    .bearish { color: #FF4B4B; font-weight: bold; }
    .header-box { background: rgba(30,144,255,0.05); padding: 15px; border-radius: 12px; border: 1px solid #1E90FF; text-align: center; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="5d", interval="4h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

# --- 5. HEADER: WÄHRUNGEN & INDIZES ---
st.title("🚀 Bio-Trading Monitor Live PRO")

st.subheader("💱 Währungen & 📈 Indizes")
# Wir erstellen eine feste Anzahl an Spalten für die erste Sektion
h_cols = st.columns(6)
header_tickers = ["EURUSD=X", "EURRUB=X", "^GDAXI", "^STOXX50E", "^NDX", "XU100.IS"]

for i, t in enumerate(header_tickers):
    df_h = get_data(t)
    if not df_h.empty:
        l = float(df_h['Close'].iloc[-1]); c = ((l/df_h['Close'].iloc[-2])-1)*100
        fmt = ":,.5f" if "=X" in t else ":,.2f"
        color_class = "bullish" if c > 0 else "bearish"
        h_cols[i].markdown(f'''
            <div class="market-card">
                <small>{TICKER_NAMES.get(t,t)}</small><br>
                <span class="metric-value">{format(l, fmt.replace(":",""))}</span><br>
                <span class="{color_class}">{c:+.2f}%</span>
            </div>''', unsafe_allow_html=True)

st.divider()

# --- 6. MONTE CARLO & WETTER-LOGIK ---
if 'sel_market' not in st.session_state: st.session_state.sel_market = "DAX 40 (DE)"
if 'sel_stock' not in st.session_state: st.session_state.sel_stock = "SAP.DE"

d_s = get_data(st.session_state.sel_stock, period="60d")
if not d_s.empty:
    cp = float(d_s['Close'].iloc[-1])
    trend_5d = ((cp / d_s['Close'].iloc[-5]) - 1) * 100
    
    # Wetter-Logik: Call (C) / Put (P)
    label, icon, color = ("(C)", "☀️", "#00FFA3") if trend_5d > 0 else ("(P)", "⛈️", "#FF4B4B")
    target = cp * 1.05; sl_dist = -3.00

    # Fokus-Balken mit Aktionsfarben
    st.markdown(f"""
        <div class="header-box">
            <span style="color:#8892b0;">Fokus:</span> <b style="color:white; font-size:1.2rem;">{TICKER_NAMES.get(st.session_state.sel_stock, st.session_state.sel_stock)}</b> 
            <span style="color:#1E90FF; margin: 0 15px;">|</span>
            <span style="color:#8892b0;">Kurs:</span> <b style="color:white; font-size:1.2rem;">{cp:,.2f}</b> 
            <span style="color:#1E90FF; margin: 0 15px;">|</span>
            <span style="color:{color}; font-weight:bold; font-size:1.2rem;">{label} Ziel: {target:,.2f} 
            <span style="font-size:0.9rem; color:#8892b0;">({sl_dist:+.2f}% SL)</span> {icon}</span>
        </div>
    """, unsafe_allow_html=True)

    # Chart
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
    log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)); vol = log_returns.std()
    for _ in range(20):
        p = [cp]; 
        for _ in range(25): p.append(p[-1] * np.exp(np.random.normal(0, vol)))
        ax.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.15)
    st.pyplot(fig)

# --- 7. SCANNER (DARUNTER) ---
st.subheader(f"🎯 Scanner: {st.session_state.sel_market}")
# Scanner-Logik hier einfügen... (Top 5 Calls / Puts)

# --- 8. STEUERUNG (GANZ UNTEN) ---
st.divider()
st.subheader("⚙️ Steuerung")
cs1, cs2 = st.columns(2)
st.session_state.sel_market = cs1.selectbox("Markt:", list(TICKER_GROUPS.keys()))
st.session_state.sel_stock = cs2.selectbox("Aktie:", TICKER_GROUPS[st.session_state.sel_market], format_func=lambda x: TICKER_NAMES.get(x, x))
