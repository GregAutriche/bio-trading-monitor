import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Pro", layout="wide")

# --- 2. DESIGN: DUNKELBLAUER LOOK & GLASSMORPHISM CSS ---
st.markdown("""
    <style>
    /* Haupt-Hintergrund */
    .stApp {
        background-color: #0E1117;
        background-image: linear-gradient(180deg, #0e1525 0%, #050a14 100%);
        color: #E0E0E0;
    }
    
    /* Glassmorphism Karten-Stil */
    .market-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease-in-out;
    }
    .market-card:hover {
        transform: translateY(-3px);
        border: 1px solid rgba(30, 144, 255, 0.4);
    }
    .metric-value { font-size: 1.4rem; font-weight: bold; color: #FFFFFF; }
    .metric-change { font-size: 0.9rem; }

    /* Sidebar News-Ticker Animation */
    .news-container { height: 400px; overflow: hidden; position: relative; border-left: 2px solid rgba(30, 144, 255, 0.3); padding-left: 10px; }
    .news-scroll { animation: scroll-up 25s linear infinite; }
    .news-scroll:hover { animation-play-state: paused; }
    .news-item { margin-bottom: 20px; font-size: 0.85rem; background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 8px; }
    @keyframes scroll-up { 0% { transform: translateY(0); } 100% { transform: translateY(-50%); } }
    
    /* Header Fixes */
    h1, h2, h3 { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKTIONEN ---
@st.cache_data(ttl=600)
def get_market_data(ticker, interval="1d", period="60d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False, timeout=15)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=1800)
def get_stock_news(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.news[:5]
    except:
        return []

# --- 4. DATEN-STRUKTUREN ---
SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", "DAX Index": "^GDAXI", "EuroStoxx 50": "^STOXX50E", 
    "S&P 500": "^GSPC", "Bitcoin": "BTC-USD"
}

STOCKS_BY_INDEX = {
    "DAX": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "BMW.DE"],
    "NASDAQ": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA"],
    "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "LIN.DE"],
    "BIST 100": ["THYAO.IS", "ASELS.IS", "KCHOL.IS", "EREGL.IS"],
    "Nifty 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]
}

# --- 5. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Pro")

# SEKTION 1: GLOBALER MARKT-FRAMEWORK
st.subheader("1. Globales Markt-Framework")
cols = st.columns(len(SYMBOLS_GENERAL))

for i, (name, ticker) in enumerate(SYMBOLS_GENERAL.items()):
    df_gen = get_market_data(ticker, interval="1d", period="5d")
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        color = "#00FFA3" if change > 0 else "#FF4B4B"
        val_str = f"{last_c:.4f}" if "/" in name else f"{last_c:,.0f}"

        with cols[i]:
            st.markdown(f"""
                <div class="market-card">
                    <div style="font-size: 0.8rem; color: #8892b0;">{name}</div>
                    <div class="metric-value">{val_str}</div>
                    <div class="metric-change" style="color: {color};">{change:+.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

# SEKTION 2: AKTIEN-ANALYSE
st.divider()
col_main, col_side = st.columns([2, 1])

with col_main:
    st.subheader("2. Deep-Dive Analyse")
    c1, c2 = st.columns(2)
    selected_idx = c1.selectbox("Index wählen:", list(STOCKS_BY_INDEX.keys()))
    selected_stock = c2.selectbox("Aktie wählen:", STOCKS_BY_INDEX[selected_idx])

    if selected_stock:
        stock_data = get_market_data(selected_stock, interval="4h", period="60d")
        if not stock_data.empty and len(stock_data) > 14:
            current_p = float(stock_data['Close'].iloc[-1])
            
            # Monte Carlo Simulation
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#0E1117')
            ax.set_facecolor('#0E1117')
            
            returns = stock_data['Close'].pct_change().dropna()
            daily_vol = returns.std()
            sim_ends = []
            
            for _ in range(100):
                prices = [current_p]
                for _ in range(30):
                    prices.append(prices[-1] * (1 + np.random.normal(0, daily_vol)))
                path_color = '#00FFA3' if prices[-1] > current_p else '#FF4B4B'
                ax.plot(prices, color=path_color, alpha=0.15)
                sim_ends.append(prices[-1])
            
            ax.axhline(y=current_p, color='white', linestyle='--', alpha=0.3)
            st.pyplot(fig)

            # Wahrscheinlichkeits-Box
            sim_ends_arr = np.array(sim_ends)
            prob_up = (sim_ends_arr > current_p).mean() * 100
            st.markdown(f"""
                <div style="background: rgba(30, 144, 255, 0.1); border-radius: 10px; padding: 15px; border: 1px solid rgba(30, 144, 255, 0.3); text-align: center;">
                    <span style="color: #1E90FF;">Wahrscheinlichkeit für Kursanstieg (30 Tage):</span>
                    <span style="font-size: 1.5rem; font-weight: bold; margin-left: 10px;">{prob_up:.1f}%</span>
                </div>
            """, unsafe_allow_html=True)

# SIDEBAR: NEWS TICKER
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com", width=50)
    st.title("Market Hub")
    st.divider()
    st.subheader(f"🗞️ News: {selected_stock}")
    
    news_list = get_stock_news(selected_stock)
    if news_list:
        news_html = "".join([f'<div class="news-item"><a href="{n["link"]}" target="_blank" style="text-decoration:none; color:#1E90FF; font-weight:bold;">{n["title"]}</a><br><small>Quelle: {n["publisher"]}</small></div>' for n in news_list])
        st.markdown(f'<div class="news-container"><div class="news-scroll">{news_html}{news_html}</div></div>', unsafe_allow_html=True)
    
    st.info(f"Streamlit v{st.__version__}\nDaten von Yahoo Finance")
