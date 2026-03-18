import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")

# AUTO-REFRESH: Die App aktualisiert sich alle 60 Sekunden von selbst
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. NAMENS-MAPPING (Vollständiger DAX 40 & NASDAQ Top-Werte) ---
TICKER_NAMES = {
    # Forex & Indices
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB",
    "^GDAXI": "DAX Index", "^STOXX50E": "EuroStoxx 50",
    "^NSEI": "Nifty 50", "XU100.IS": "BIST 100",
    
    # DAX 40
    "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer",
    "BMW.DE": "BMW", "CON.DE": "Continental", "1COV.DE": "Covestro", "DTG.DE": "Daimler Truck",
    "DBK.DE": "Deutsche Bank", "DB1.DE": "Deutsche Börse", "LHA.DE": "Lufthansa", "DTE.DE": "Telekom",
    "EON.DE": "E.ON", "FME.DE": "Fresenius Med.", "FRE.DE": "Fresenius SE", "HLAG.DE": "Hapag-Lloyd",
    "HNR1.DE": "Hannover Rück", "HEI.DE": "Heidelberg Materials", "HFG.DE": "HelloFresh", "HEN3.DE": "Henkel",
    "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "MRK.DE": "Merck KGaA", "MTX.DE": "MTU Aero",
    "MUV2.DE": "Münchener Rück", "PUM.DE": "Puma", "RHM.DE": "Rheinmetall", "RWE.DE": "RWE",
    "SAP.DE": "SAP SE", "SIE.DE": "Siemens AG", "SRT3.DE": "Sartorius", "SHL.DE": "Siemens Health",
    "SY1.DE": "Symrise", "VOW3.DE": "Volkswagen", "VNA.DE": "Vonovia", "ZAL.DE": "Zalando", "BEI.DE": "Beiersdorf",
    "MTX.DE": "MTU Aero Engines", "QIA.DE": "Qiagen", "WIE.DE": "Wienerberger",

    # NASDAQ Top Tech
    "AAPL": "Apple Inc.", "MSFT": "Microsoft", "NVDA": "Nvidia", "TSLA": "Tesla", "AMZN": "Amazon",
    "GOOGL": "Alphabet", "META": "Meta", "AVGO": "Broadcom", "NFLX": "Netflix", "AMD": "AMD"
}

# --- 3. DESIGN: DUNKELBLAU & GLASSMORPHISM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; background-image: linear-gradient(180deg, #0e1525 0%, #050a14 100%); color: #E0E0E0; }
    .market-card {
        background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 15px; margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(8px); transition: 0.2s;
    }
    .market-card:hover { transform: translateY(-3px); border: 1px solid rgba(30, 144, 255, 0.4); }
    .metric-value { font-size: 1.15rem; font-weight: bold; color: #FFFFFF; font-family: 'Courier New', monospace; }
    
    .news-container { height: 400px; overflow: hidden; position: relative; border-left: 2px solid #1E90FF; padding-left: 12px; }
    .news-scroll { animation: scroll-up 40s linear infinite; }
    .news-scroll:hover { animation-play-state: paused; }
    .news-item { margin-bottom: 15px; font-size: 0.85rem; background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 8px; line-height: 1.4; }
    @keyframes scroll-up { 0% { transform: translateY(0); } 100% { transform: translateY(-50%); } }
    h1, h2, h3 { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN (Mit Fallback-Logik) ---
@st.cache_data(ttl=60)
def get_market_data(ticker, period="60d", interval="1d"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

@st.cache_data(ttl=1800)
def get_news_with_fallback(ticker):
    try:
        # 1. Versuch: Firmenspezifische News
        s = yf.Ticker(ticker)
        news = [n for n in s.news if n.get('title')]
        
        # 2. Versuch (Fallback): Wenn leer, nimm allgemeine DAX-Markt-News
        if not news:
            market = yf.Ticker("^GDAXI")
            news = [n for n in market.news if n.get('title')]
            for n in news: n['is_fallback'] = True
        return news[:12]
    except: return []

# --- 5. DATENSTRUKTUR ---
SYMBOLS_GENERAL = ["EURUSD=X", "EURRUB=X", "^GDAXI", "^STOXX50E", "^NSEI", "XU100.IS"]
STOCKS_BY_INDEX = {
    "DAX (Alle 40)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
    "NASDAQ Tech": ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "AVGO", "NFLX", "AMD"],
    "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "SIE.DE"],
    "BIST 100": ["THYAO.IS", "ASELS.IS", "KCHOL.IS"],
    "Nifty 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
}

# --- 6. LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")
st.caption(f"Status: Live | Letztes Update: {pd.Timestamp.now().strftime('%H:%M:%S')}")

# SEKTION 1: GLOBALER MARKT-FRAMEWORK
cols = st.columns(len(SYMBOLS_GENERAL))
for i, t in enumerate(SYMBOLS_GENERAL):
    df = get_market_data(t, period="5d")
    if not df.empty and len(df) >= 2:
        last = float(df['Close'].iloc[-1])
        chg = ((last / df['Close'].iloc[-2]) - 1) * 100
        fmt = "{:,.5f}" if "=X" in t else "{:,.2f}"
        with cols[i]:
            st.markdown(f"""
                <div class="market-card">
                    <div style="font-size:0.75rem; color:#8892b0;">{"☀️" if chg>0 else "🌧️"} {TICKER_NAMES.get(t,t)}</div>
                    <div class="metric-value">{fmt.format(last)}</div>
                    <div style="color:{"#00FFA3" if chg>0 else "#FF4B4B"}; font-size:0.8rem;">{chg:+.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

# SEKTION 2: ANALYSE & DYNAMISCHE NEWS
st.divider()
c_main, c_news = st.columns([2, 1])

with c_main:
    st.subheader("📊 Deep-Dive & Monte Carlo")
    ca, cb = st.columns(2)
    sel_idx = ca.selectbox("Index wählen:", list(STOCKS_BY_INDEX.keys()))
    sel_tkr = cb.selectbox("Aktie wählen:", STOCKS_BY_INDEX[sel_idx], format_func=lambda x: TICKER_NAMES.get(x, x))
    
    data = get_market_data(sel_tkr, interval="4h")
    if not data.empty:
        cp = float(data['Close'].iloc[-1])
        mom = data['Close'].iloc[-1] - data['Close'].iloc[-14]
        
        # Monte Carlo Simulation
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#0E1117')
        ax.set_facecolor('#0E1117')
        ends = []
        for _ in range(70):
            p = [cp]
            for _ in range(30): p.append(p[-1] * (1 + np.random.normal(0, data['Close'].pct_change().std())))
            ax.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.15)
            ends.append(p[-1])
        ax.axhline(y=cp, color='white', linestyle='--', alpha=0.3)
        st.pyplot(fig)

        # Aktions-Empfehlung
        prob_up = (np.array(ends) > cp).mean() * 100
        n = TICKER_NAMES.get(sel_tkr, sel_tkr)
        if mom > 0 and prob_up > 55: st.success(f"🟢 **KAUFEN:** {n} (Starker Trend & {prob_up:.1f}% Aufwärts-Chance)")
        elif mom < 0 and prob_up < 45: st.error(f"🔴 **VERKAUFEN:** {n} (Abwärtstrend)")
        else: st.warning(f"🟡 **HALTEN:** {n} (Neutrales Umfeld)")

with c_news:
    # News-Logik mit Fallback
    n_list = get_news_with_fallback(sel_tkr)
    is_fb = any(n.get('is_fallback') for n in n_list)
    st.subheader("🌍 Global Markt News" if is_fb else f"🗞️ {TICKER_NAMES.get(sel_tkr, sel_tkr)} News")
    
    if n_list:
        h = ""
        for i in n_list:
            link = i.get("link") or i.get("resolvedUrl") or "#"
            title = i.get("title") or i.get("summary") or "Kein Titel"
            h += f'<div class="news-item"><a href="{link}" target="_blank" style="color:#1E90FF; text-decoration:none;">{title[:85]}..</a></div>'
        st.markdown(f'<div class="news-container"><div class="news-scroll">{h}{h}</div></div>', unsafe_allow_html=True)
    else: st.info("Keine News verfügbar.")
