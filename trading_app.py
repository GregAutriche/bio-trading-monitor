import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Pro", layout="wide")

# --- 2. DESIGN & GLASSMORPHISM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; background-image: linear-gradient(180deg, #0e1525 0%, #050a14 100%); color: #E0E0E0; }
    .market-card {
        background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 15px; margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); transition: transform 0.2s;
    }
    .market-card:hover { transform: translateY(-3px); border: 1px solid rgba(30, 144, 255, 0.4); }
    .metric-value { font-size: 1.4rem; font-weight: bold; color: #FFFFFF; }
    .news-container { height: 350px; overflow: hidden; position: relative; border-left: 2px solid #1E90FF; padding-left: 10px; }
    .news-scroll { animation: scroll-up 30s linear infinite; }
    .news-scroll:hover { animation-play-state: paused; }
    .news-item { margin-bottom: 15px; font-size: 0.8rem; background: rgba(255, 255, 255, 0.05); padding: 8px; border-radius: 8px; }
    @keyframes scroll-up { 0% { transform: translateY(0); } 100% { transform: translateY(-50%); } }
    h1, h2, h3 { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKTIONEN (Sicherer Zugriff auf News) ---
@st.cache_data(ttl=600)
def get_market_data(ticker, interval="1d", period="60d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        return data
    except: return pd.DataFrame()

@st.cache_data(ttl=1800)
def get_stock_news(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.news[:8]
    except: return []

# --- 4. DATEN ---
SYMBOLS_GENERAL = {"EUR/USD": "EURUSD=X", "DAX": "^GDAXI", "S&P 500": "^GSPC", "Bitcoin": "BTC-USD"}
STOCKS_BY_INDEX = {
    "DAX": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE"],
    "NASDAQ": ["AAPL", "MSFT", "NVDA", "TSLA"],
}

# --- 5. DASHBOARD ---
st.title("🚀 Bio-Trading Monitor Pro")

# SEKTION 1: MARKT-FRAMEWORK MIT WETTER
st.subheader("1. Markt-Wetter")
cols = st.columns(len(SYMBOLS_GENERAL))
for i, (name, ticker) in enumerate(SYMBOLS_GENERAL.items()):
    df = get_market_data(ticker, period="5d")
    if not df.empty:
        change = ((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100
        weather = "☀️" if change > 0 else "🌧️"
        color = "#00FFA3" if change > 0 else "#FF4B4B"
        with cols[i]:
            st.markdown(f'<div class="market-card"><div style="font-size:1.2rem;">{weather} {name}</div>'
                        f'<div class="metric-value">{df["Close"].iloc[-1]:,.2f}</div>'
                        f'<div style="color:{color};">{change:+.2f}%</div></div>', unsafe_allow_html=True)

# SEKTION 2: ANALYSE & SIGNALE
st.divider()
c_main, c_news = st.columns([2, 1])

with c_main:
    idx = st.selectbox("Index:", list(STOCKS_BY_INDEX.keys()))
    stock_sym = st.selectbox("Aktie:", STOCKS_BY_INDEX[idx])
    
    data = get_market_data(stock_sym, interval="4h")
    if not data.empty:
        curr_p = float(data['Close'].iloc[-1])
        # Einfaches Momentum-Signal
        mom = data['Close'].iloc[-1] - data['Close'].iloc[-14]
        
        # Monte Carlo Simulation
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#0E1117')
        ax.set_facecolor('#0E1117')
        sim_ends = []
        for _ in range(50):
            p = [curr_p]
            for _ in range(30): p.append(p[-1] * (1 + np.random.normal(0, data['Close'].pct_change().std())))
            ax.plot(p, color='#00FFA3' if p[-1] > curr_p else '#FF4B4B', alpha=0.2)
            sim_ends.append(p[-1])
        st.pyplot(fig)

        # AKTIONSSYMBOLE & EMPFEHLUNG
        prob_up = (np.array(sim_ends) > curr_p).mean() * 100
        if mom > 0 and prob_up > 55:
            st.success(f"🟢 **AKTION: KAUFEN** (Momentum +{mom:.2f} | Chance: {prob_up:.1f}%)")
        elif mom < 0 and prob_up < 45:
            st.error(f"🔴 **AKTION: VERKAUFEN** (Momentum {mom:.2f} | Chance: {prob_up:.1f}%)")
        else:
            st.warning(f"🟡 **AKTION: HALTEN** (Neutrales Umfeld)")

with c_news:
    st.subheader(f"🗞️ {stock_sym} News")
    news = get_stock_news(stock_sym)
    if news:
        items_html = ""
        for n in news:
            # SICHERER ZUGRIFF: Falls 'link' fehlt, nutze Alternative oder Platzhalter
            link = n.get('link') or n.get('resolvedUrl') or "#"
            title = n.get('title', 'Kein Titel verfügbar')
            items_html += f'<div class="news-item"><a href="{link}" target="_blank" style="color:#1E90FF;">{title}</a></div>'
        
        st.markdown(f'<div class="news-container"><div class="news-scroll">{items_html}{items_html}</div></div>', unsafe_allow_html=True)
