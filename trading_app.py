import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Pro", layout="wide")

# --- 2. NAMENS-MAPPING & TICKER ---
TICKER_NAMES = {
    "EURUSD=X": "Euro / US-Dollar",
    "EURRUB=X": "Euro / Russischer Rubel",
    "^GDAXI": "DAX Index",
    "^GSPC": "S&P 500",
    "BTC-USD": "Bitcoin",
    "SAP.DE": "SAP SE",
    "SIE.DE": "Siemens AG",
    "ALV.DE": "Allianz SE",
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "NVDA": "Nvidia Corp."
}

# --- 3. DESIGN & CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; background-image: linear-gradient(180deg, #0e1525 0%, #050a14 100%); color: #E0E0E0; }
    .market-card {
        background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 15px; margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); transition: transform 0.2s;
    }
    .market-card:hover { transform: translateY(-3px); border: 1px solid rgba(30, 144, 255, 0.4); }
    .metric-value { font-size: 1.25rem; font-weight: bold; color: #FFFFFF; font-family: 'Courier New', monospace; }
    .news-container { height: 350px; overflow: hidden; position: relative; border-left: 2px solid #1E90FF; padding-left: 10px; }
    .news-scroll { animation: scroll-up 35s linear infinite; }
    .news-scroll:hover { animation-play-state: paused; }
    .news-item { margin-bottom: 15px; font-size: 0.8rem; background: rgba(255, 255, 255, 0.05); padding: 8px; border-radius: 8px; }
    @keyframes scroll-up { 0% { transform: translateY(0); } 100% { transform: translateY(-50%); } }
    h1, h2, h3 { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
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

# --- 5. DATENSTRUKTUR ---
# Jetzt inklusive EUR/RUB
SYMBOLS_GENERAL = ["EURUSD=X", "EURRUB=X", "^GDAXI", "BTC-USD"]
STOCKS_BY_INDEX = {
    "DAX": ["SAP.DE", "SIE.DE", "ALV.DE"],
    "NASDAQ": ["AAPL", "MSFT", "NVDA"],
}

# --- 6. DASHBOARD ---
st.title("🚀 Bio-Trading Monitor Pro")

# SEKTION 1: MARKT-WETTER (Mit 5 Nachkommastellen für FX)
st.subheader("1. Markt-Wetter")
cols = st.columns(len(SYMBOLS_GENERAL))

for i, ticker in enumerate(SYMBOLS_GENERAL):
    df = get_market_data(ticker, period="5d")
    if not df.empty:
        last_price = float(df['Close'].iloc[-1])
        change = ((last_price / df['Close'].iloc[-2]) - 1) * 100
        weather = "☀️" if change > 0 else "🌧️"
        color = "#00FFA3" if change > 0 else "#FF4B4B"
        full_name = TICKER_NAMES.get(ticker, ticker)
        
        # LOGIK FÜR NACHKOMMASTELLEN:
        # Wenn "=X" im Ticker (Währungen), dann 5 Stellen, sonst 2.
        format_str = "{:,.5f}" if "=X" in ticker else "{:,.2f}"
        val_display = format_str.format(last_price)

        with cols[i]:
            st.markdown(f"""
                <div class="market-card">
                    <div style="font-size:0.85rem; color:#8892b0; margin-bottom:5px;">{weather} {full_name}</div>
                    <div class="metric-value">{val_display}</div>
                    <div style="color:{color}; font-size:0.9rem; margin-top:5px;">{change:+.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

# SEKTION 2: ANALYSE
st.divider()
c_main, c_news = st.columns([2, 1]) 

with c_main:
    st.subheader("2. Deep-Dive Analyse")
    idx_col, stock_col = st.columns(2)
    selected_idx = idx_col.selectbox("Index wählen:", list(STOCKS_BY_INDEX.keys()))
    selected_stock = stock_col.selectbox(
        "Aktie wählen:", 
        STOCKS_BY_INDEX[selected_idx],
        format_func=lambda x: TICKER_NAMES.get(x, x)
    )
    
    data = get_market_data(selected_stock, interval="4h")
    if not data.empty:
        curr_p = float(data['Close'].iloc[-1])
        mom = data['Close'].iloc[-1] - data['Close'].iloc[-14]
        
        # Monte Carlo Simulation Plot
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#0E1117')
        ax.set_facecolor('#0E1117')
        sim_ends = []
        for _ in range(60):
            p = [curr_p]
            for _ in range(30): p.append(p[-1] * (1 + np.random.normal(0, data['Close'].pct_change().std())))
            ax.plot(p, color='#00FFA3' if p[-1] > curr_p else '#FF4B4B', alpha=0.15)
            sim_ends.append(p[-1])
        ax.axhline(y=curr_p, color='white', linestyle='--', alpha=0.3)
        st.pyplot(fig)

        # AKTIONSSYMBOLE
        prob_up = (np.array(sim_ends) > curr_p).mean() * 100
        stock_display_name = TICKER_NAMES.get(selected_stock, selected_stock)
        
        if mom > 0 and prob_up > 55:
            st.success(f"🟢 **AKTION: KAUFEN** ({stock_display_name} mit positivem Trend)")
        elif mom < 0 and prob_up < 45:
            st.error(f"🔴 **AKTION: VERKAUFEN** ({stock_display_name} mit negativem Trend)")
        else:
            st.warning(f"🟡 **AKTION: HALTEN** (Neutrales Signal für {stock_display_name})")

with c_news:
    st.subheader(f"🗞️ {TICKER_NAMES.get(selected_stock, selected_stock)} News")
    news_items = get_stock_news(selected_stock)
    if news_items:
        html = ""
        for n in news_items:
            link = n.get('link') or n.get('resolvedUrl') or "#"
            title = n.get('title', 'Kein Titel')
            html += f'<div class="news-item"><a href="{link}" target="_blank" style="color:#1E90FF; text-decoration:none;">{title}</a></div>'
        st.markdown(f'<div class="news-container"><div class="news-scroll">{html}{html}</div></div>', unsafe_allow_html=True)
