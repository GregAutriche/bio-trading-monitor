import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")

# AUTO-REFRESH: Alle 60 Sekunden
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. VOLLSTÄNDIGES NAMENS-MAPPING (DAX 40 & NASDAQ Top) ---
TICKER_NAMES = {
    # Forex & Indices
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB",
    "^GDAXI": "DAX Index", "^STOXX50E": "EuroStoxx 50",
    "^NSEI": "Nifty 50", "XU100.IS": "BIST 100",
    
    # DAX 40 (Auswahl der wichtigsten & neuen Werte 2026)
    "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer",
    "BMW.DE": "BMW", "CON.DE": "Continental", "1COV.DE": "Covestro", "DTG.DE": "Daimler Truck",
    "DBK.DE": "Deutsche Bank", "DB1.DE": "Deutsche Börse", "LHA.DE": "Lufthansa", "DTE.DE": "Telekom",
    "EON.DE": "E.ON", "FME.DE": "Fresenius Med.", "FRE.DE": "Fresenius SE", "HLAG.DE": "Hapag-Lloyd",
    "HNR1.DE": "Hannover Rück", "HEI.DE": "Heidelberg Materials", "HFG.DE": "HelloFresh", "HEN3.DE": "Henkel",
    "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "MRK.DE": "Merck KGaA", "MTX.DE": "MTU Aero",
    "MUV2.DE": "Münchener Rück", "PUM.DE": "Puma", "RHM.DE": "Rheinmetall", "RWE.DE": "RWE",
    "SAP.DE": "SAP SE", "SIE.DE": "Siemens AG", "SRT3.DE": "Sartorius", "SHL.DE": "Siemens Health",
    "SY1.DE": "Symrise", "VOW3.DE": "Volkswagen", "VNA.DE": "Vonovia", "ZAL.DE": "Zalando",

    # NASDAQ 100 Top-Werte
    "AAPL": "Apple Inc.", "MSFT": "Microsoft", "NVDA": "Nvidia", "TSLA": "Tesla", "AMZN": "Amazon",
    "GOOGL": "Alphabet (Google)", "META": "Meta Platforms", "AVGO": "Broadcom", "COST": "Costco",
    "NFLX": "Netflix", "AMD": "AMD", "INTC": "Intel", "PYPL": "PayPal"
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; background-image: linear-gradient(180deg, #0e1525 0%, #050a14 100%); color: #E0E0E0; }
    .market-card {
        background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 15px; margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(8px); transition: 0.2s;
    }
    .metric-value { font-size: 1.15rem; font-weight: bold; color: #FFFFFF; font-family: 'Courier New', monospace; }
    .news-container { height: 400px; overflow: hidden; border-left: 2px solid #1E90FF; padding-left: 12px; }
    .news-scroll { animation: scroll-up 40s linear infinite; }
    .news-scroll:hover { animation-play-state: paused; }
    .news-item { margin-bottom: 15px; font-size: 0.85rem; background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 8px; }
    @keyframes scroll-up { 0% { transform: translateY(0); } 100% { transform: translateY(-50%); } }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="1d"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

@st.cache_data(ttl=600)
def get_news(ticker):
    try:
        s = yf.Ticker(ticker)
        return [n for n in s.news if n.get('title')][:12]
    except: return []

# --- 5. STRUKTUR ---
SYMBOLS_GENERAL = ["EURUSD=X", "EURRUB=X", "^GDAXI", "^STOXX50E", "^NSEI", "XU100.IS"]
STOCKS_BY_INDEX = {
    "DAX (Alle 40)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
    "NASDAQ (Top Tech)": ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "AVGO", "NFLX", "AMD"],
    "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "SIE.DE"],
    "BIST 100": ["THYAO.IS", "ASELS.IS", "KCHOL.IS"],
    "Nifty 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
}

# --- 6. LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")
st.caption(f"Status: Live | Letztes Daten-Update: {pd.Timestamp.now().strftime('%H:%M:%S')}")

# SEKTION 1: MARKT-WETTER
cols = st.columns(len(SYMBOLS_GENERAL))
for i, t in enumerate(SYMBOLS_GENERAL):
    df = get_data(t, period="5d")
    if not df.empty:
        last = float(df['Close'].iloc[-1])
        chg = ((last / df['Close'].iloc[-2]) - 1) * 100
        fmt = "{:,.5f}" if "=X" in t else "{:,.2f}"
        with cols[i]:
            st.markdown(f'<div class="market-card"><div style="font-size:0.75rem; color:#8892b0;">{"☀️" if chg>0 else "🌧️"} {TICKER_NAMES.get(t,t)}</div>'
                        f'<div class="metric-value">{fmt.format(last)}</div>'
                        f'<div style="color:{"#00FFA3" if chg>0 else "#FF4B4B"}; font-size:0.8rem;">{chg:+.2f}%</div></div>', unsafe_allow_html=True)

# SEKTION 2: ANALYSE
st.divider()
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📊 Deep-Dive Analyse")
    ca, cb = st.columns(2)
    s_idx = ca.selectbox("Index wählen:", list(STOCKS_BY_INDEX.keys()))
    s_tkr = cb.selectbox("Aktie wählen:", STOCKS_BY_INDEX[s_idx], format_func=lambda x: TICKER_NAMES.get(x, x))
    
    d_stock = get_data(s_tkr, interval="4h")
    if not d_stock.empty:
        cp = float(d_stock['Close'].iloc[-1])
        mom = d_stock['Close'].iloc[-1] - d_stock['Close'].iloc[-14]
        
        # Monte Carlo
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#0E1117')
        ax.set_facecolor('#0E1117')
        ends = []
        for _ in range(70):
            p = [cp]
            for _ in range(30): p.append(p[-1] * (1 + np.random.normal(0, d_stock['Close'].pct_change().std())))
            ax.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.12)
            ends.append(p[-1])
        ax.axhline(y=cp, color='white', linestyle='--', alpha=0.3)
        st.pyplot(fig)

        prob_up = (np.array(ends) > cp).mean() * 100
        n = TICKER_NAMES.get(s_tkr, s_tkr)
        if mom > 0 and prob_up > 55: st.success(f"🟢 **KAUFEN:** {n} (Starker Trend)")
        elif mom < 0 and prob_up < 45: st.error(f"🔴 **VERKAUFEN:** {n} (Abwärtstrend)")
        else: st.warning(f"🟡 **HALTEN:** {n} (Seitwärts)")

with c2:
    st.subheader(f"🗞️ {TICKER_NAMES.get(s_tkr, s_tkr)} News")
    n_list = get_news(s_tkr)
    if n_list:
        h = "".join(}..</a></div>' for i in n_list])
        st.markdown(f'<div class="news-container"><div class="news-scroll">{h}{h}</div></div>', unsafe_allow_html=True)
    else: st.info("Keine News.")
