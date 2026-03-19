import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. VOLLSTÄNDIGE TICKER-LISTEN ---
# DAX 40, EuroStoxx 50, NASDAQ 100, BIST 100, Nifty 50
TICKER_GROUPS = {
    "DAX 40 (DE)": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "BNR.DE", "CBK.DE", "CON.DE", "1COV.DE", "DTG.DE", "DBK.DE", "DB1.DE", "DHL.DE", "DTE.DE", "EON.DE", "FME.DE", "FRE.DE", "GEA.DE", "HNR1.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "PAH3.DE", "PUM.DE", "QIA.DE", "RHM.DE", "RWE.DE", "SAP.DE", "SIE.DE", "ENR.DE", "SHL.DE", "SY1.DE", "VOW3.DE", "VNA.DE", "ZAL.DE"],
    "EuroStoxx 50 (EU)": ["ADYEN.AS", "AD.AS", "AI.PA", "AIR.PA", "ALV.DE", "ASML.AS", "CS.PA", "BAS.DE", "BAYN.DE", "BBVA.MC", "SAN.MC", "BMW.DE", "BNP.PA", "CRG.IR", "DHL.DE", "DTE.DE", "ENEL.MI", "ENI.MI", "EL.PA", "FLTR.L", "RMS.PA", "IBE.MC", "ITX.MC", "IFX.DE", "INGA.AS", "ISP.MI", "KER.PA", "OR.PA", "MC.PA", "MBG.DE", "MUV2.DE", "NOKIA.HE", "RI.PA", "PRX.AS", "SAF.PA", "SAN.PA", "SAP.DE", "SU.PA", "SIE.DE", "STLAM.MI", "TTE.PA", "DG.PA", "VOW3.DE", "VNA.DE", "VIV.PA"],
    "NASDAQ 100 (US)": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "COST", "NFLX", "AMD", "ADBE", "PEP", "CSCO", "INTC", "TMUS", "INTU", "AMGN", "QCOM", "ISRG"],
    "BIST 100 (TR)": ["THYAO.IS", "ASELS.IS", "KCHOL.IS", "EREGL.IS", "AKBNK.IS", "TUPRS.IS", "BIMAS.IS", "GARAN.IS", "SISE.IS", "SAHOL.IS"],
    "Nifty 50 (IN)": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "BHARTIARTL.NS", "LICI.NS", "ITC.NS", "LT.NS"]
}

# Mapping für lesbare Namen (Auszug)
TICKER_NAMES = {"EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50", "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50"}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; color: white; }
    .bullish { color: #00FFA3; font-weight: bold; }
    .bearish { color: #FF4B4B; font-weight: bold; }
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

def get_options_data(ticker_str):
    try:
        tk = yf.Ticker(ticker_str)
        if not tk.options: return None, None
        opt = tk.option_chain(tk.options)
        return opt.calls.sort_values("openInterest", ascending=False).head(5)[['strike', 'openInterest']], \
               opt.puts.sort_values("openInterest", ascending=False).head(5)[['strike', 'openInterest']]
    except: return None, None

# --- 5. HEADER (WÄHRUNGEN & INDIZES) ---
st.title("🚀 Bio-Trading Monitor Live PRO")

st.subheader("💱 Währungen")
cf1, cf2, _ = st.columns([1,1,4])
for i, t in enumerate(["EURUSD=X", "EURRUB=X"]):
    df = get_data(t, period="2d")
    if not df.empty:
        l = float(df['Close'].iloc[-1]); c = ((l/df['Close'].iloc[-2])-1)*100
        (cf1 if i==0 else cf2).markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.5f}</span> <span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

st.subheader("📈 Markt-Indizes")
cols_i = st.columns(5)
for i, t in enumerate(["^GDAXI", "^STOXX50E", "^NDX", "XU100.IS", "^NSEI"]):
    df = get_data(t, period="2d")
    if not df.empty:
        l = float(df['Close'].iloc[-1]); c = ((l/df['Close'].iloc[-2])-1)*100
        cols_i[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.2f}</span> <span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

# --- 6. HAUPTBEREICH (DROP-DOWNS & CHART/OPTIONS) ---
st.divider()
ca, cb = st.columns(2)
market_sel = ca.selectbox("Markt wählen:", list(TICKER_GROUPS.keys()))
stock_sel = cb.selectbox("Aktie wählen:", TICKER_GROUPS[market_sel])

c_left, c_right = st.columns([2, 1])

d_s = get_data(stock_sel)
if not d_s.empty:
    cp = float(d_s['Close'].iloc[-1])
    
    with c_left:
        st.subheader("🔮 Prognose-Wetter (Monte Carlo)")
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 5)); fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
        log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)); vol = log_returns.std()
        for _ in range(25):
            p = [cp]
            for _ in range(20): p.append(p[-1] * np.exp(np.random.normal(0, vol)))
            ax.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.15)
        ax.axhline(y=cp, color='white', linestyle='--', alpha=0.4)
        st.pyplot(fig)

    with c_right:
        st.markdown("### 🎯 Top 5 Call / Put")
        st.markdown(f"**Aktueller Kurs: {cp:,.2f}**")
        calls, puts = get_options_data(stock_sel)
        
        if calls is not None:
            st.markdown("<span class='bullish'>🟢 TOP CALLS (Widerstand)</span>", unsafe_allow_html=True)
            st.dataframe(calls.reset_index(drop=True), use_container_width=True, hide_index=True)
            st.markdown("<span class='bearish'>🔴 TOP PUTS (Unterstützung)</span>", unsafe_allow_html=True)
            st.dataframe(puts.reset_index(drop=True), use_container_width=True, hide_index=True)
        else:
            st.warning("Keine Options-Daten verfügbar (US-Ticker erforderlich).")

# --- 7. STATUS BAR UNTEN ---
st.info(f"Bio-Trading Status: {'BULLISH ☀️' if d_s['Close'].iloc[-1] > d_s['Close'].iloc[-5] else 'BEARISH ⛈️'} | Symbol: {stock_sel}")
