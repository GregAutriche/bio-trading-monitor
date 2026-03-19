import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-GRUPPEN (Indizes und zugehörige Aktien) ---
TICKER_GROUPS = {
    "DAX 40 (DE)": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "ADS.DE", "BMW.DE", "BAYN.DE", "BAS.DE", "DBK.DE", "RHM.DE"],
    "EuroStoxx 50 (EU)": ["AIR.PA", "MC.PA", "OR.PA", "ASML.AS", "SAN.PA", "BNP.PA", "TTE.PA", "ITX.MC", "ADYEN.AS"],
    "NASDAQ 100 (US)": ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "META", "GOOGL", "AMD", "NFLX", "AVGO", "COST", "QCOM"],
    "BIST 100 (TR)": ["THYAO.IS", "ASELS.IS", "KCHOL.IS", "TUPRS.IS", "BIMAS.IS", "AKBNK.IS"],
    "Nifty 50 (IN)": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS"]
}

# Mapping für Klarnamen
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50",
    "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    "SAP.DE": "SAP", "SIE.DE": "Siemens", "ALV.DE": "Allianz", "DTE.DE": "Telekom", "ADS.DE": "Adidas",
    "BMW.DE": "BMW", "BAYN.DE": "Bayer", "BAS.DE": "BASF", "DBK.DE": "Deutsche Bank", "RHM.DE": "Rheinmetall",
    "AIR.PA": "Airbus", "MC.PA": "LVMH", "OR.PA": "L'Oréal", "ASML.AS": "ASML", "SAN.PA": "Sanofi",
    "AAPL": "Apple", "NVDA": "Nvidia", "TSLA": "Tesla", "MSFT": "Microsoft", "AMZN": "Amazon",
    "THYAO.IS": "Turkish Airlines", "RELIANCE.NS": "Reliance Ind."
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; color: white; }
    .bullish { color: #00FFA3; font-weight: bold; }
    .bearish { color: #FF4B4B; font-weight: bold; }
    .header-box { background: rgba(30,144,255,0.1); padding: 15px; border-radius: 12px; border: 1px solid #1E90FF; text-align: center; margin-bottom: 20px; }
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

def run_market_scanner(ticker_list):
    results = []
    for t in ticker_list:
        df = get_data(t, period="5d")
        if not df.empty:
            cp = float(df['Close'].iloc[-1].iloc) if isinstance(df['Close'].iloc[-1], pd.Series) else float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2].iloc) if isinstance(df['Close'].iloc[-2], pd.Series) else float(df['Close'].iloc[-2])
            trend = ((cp / prev) - 1) * 100
            results.append({"Aktie": TICKER_NAMES.get(t, t), "Kurs": round(cp, 2), "Trend %": round(trend, 2)})
    return pd.DataFrame(results)

# --- 5. HEADER (Währungen & Indizes) ---
st.title("🚀 Bio-Trading Monitor Live PRO")
st.subheader("💱 Währungen & Indizes")
c1, c2, c3, c4, c5 = st.columns(5)
# ... (Anzeige-Logik für Währungen/Indizes wie bisher) ...

# --- 6. DEEP-DIVE & AUSWAHL ---
st.divider()
st.subheader("🔍 Marktanalyse & Auswahl")

# Hier ist die gewünschte Auswahl: Index wählen -> Aktie wählen
selected_index = st.selectbox("1. Aktienindex wählen:", list(TICKER_GROUPS.keys()))
selected_stock = st.selectbox("2. Aktie aus diesem Index wählen:", TICKER_GROUPS[selected_index], format_func=lambda x: TICKER_NAMES.get(x, x))

d_s = get_data(selected_stock)
if not d_s.empty:
    cp = float(d_s['Close'].iloc[-1].iloc) if isinstance(d_s['Close'].iloc[-1], pd.Series) else float(d_s['Close'].iloc[-1])
    st.markdown(f'<div class="header-box"><span style="font-size:1.3rem;">Fokus: <b>{TICKER_NAMES.get(selected_stock, selected_stock)}</b></span> | <span style="font-size:1.3rem;">Kurs: <b>{cp:,.2f}</b></span></div>', unsafe_allow_html=True)

    cl, cr = st.columns([1.5, 1])
    with cl:
        st.subheader("🔮 Bio-Prognose (Monte Carlo)")
        # ... (Monte Carlo Plot wie bisher) ...

    with cr:
        st.subheader(f"🎯 Top 5 Scanner: {selected_index}")
        with st.spinner("Scanne Signale..."):
            scan_results = run_market_scanner(TICKER_GROUPS[selected_index])
            if not scan_results.empty:
                st.markdown("<span class='bullish'>🟢 TOP CALLS</span>", unsafe_allow_html=True)
                st.dataframe(scan_results.sort_values(by="Trend %", ascending=False).head(5), hide_index=True)
                st.markdown("<span class='bearish'>🔴 TOP PUTS</span>", unsafe_allow_html=True)
                st.dataframe(scan_results.sort_values(by="Trend %", ascending=True).head(5), hide_index=True)

st.info(f"Update: {pd.Timestamp.now().strftime('%H:%M:%S')} | Status: {selected_stock}")
