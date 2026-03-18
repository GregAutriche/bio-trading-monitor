import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Pro", layout="wide")

# --- 2. NAMENS-MAPPING (Ticker -> Klarname) ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD",
    "EURRUB=X": "EUR/RUB",
    "^GDAXI": "DAX Index",
    "^STOXX50E": "EuroStoxx 50",
    "^NSEI": "Nifty 50",
    "XU100.IS": "BIST 100",
    "SAP.DE": "SAP SE", "SIE.DE": "Siemens AG", "ALV.DE": "Allianz SE", "DTE.DE": "Deutsche Telekom",
    "AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.", "NVDA": "Nvidia Corp.", "TSLA": "Tesla Inc.", "AMZN": "Amazon.com"
}

# --- 3. DESIGN: DUNKELBLAU & GLASSMORPHISM ---
st.markdown("""
    <style>
    .stApp { 
        background-color: #0E1117; 
        background-image: linear-gradient(180deg, #0e1525 0%, #050a14 100%); 
        color: #E0E0E0; 
    }
    .market-card {
        background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 15px; margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); transition: transform 0.2s;
    }
    .market-card:hover { transform: translateY(-3px); border: 1px solid rgba(30, 144, 255, 0.4); }
    .metric-value { font-size: 1.2rem; font-weight: bold; color: #FFFFFF; font-family: 'Courier New', monospace; }
    
    /* News Ticker Styling */
    .news-container { height: 380px; overflow: hidden; position: relative; border-left: 2px solid #1E90FF; padding-left: 12px; }
    .news-scroll { animation: scroll-up 35s linear infinite; }
    .news-scroll:hover { animation-play-state: paused; }
    .news-item { margin-bottom: 18px; font-size: 0.85rem; background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 8px; line-height: 1.4; }
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
        all_news = stock.news
        # Nur News mit echtem Textinhalt zulassen
        valid = [n for n in all_news if n.get('title') or n.get('summary')]
        return valid[:10]
    except: return []

# --- 5. DATENSTRUKTUR (Indices wie vereinbart) ---
SYMBOLS_GENERAL = ["EURUSD=X", "EURRUB=X", "^GDAXI", "^STOXX50E", "^NSEI", "XU100.IS"]

STOCKS_BY_INDEX = {
    "DAX": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE"],
    "NASDAQ": ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"],
    "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE"],
    "BIST 100": ["THYAO.IS", "ASELS.IS", "KCHOL.IS"],
    "Nifty 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
}

# --- 6. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Pro")

# SEKTION 1: GLOBALER MARKT-FRAMEWORK
st.subheader("1. Globales Markt-Framework")
cols = st.columns(len(SYMBOLS_GENERAL))

for i, ticker in enumerate(SYMBOLS_GENERAL):
    df = get_market_data(ticker, period="5d")
    if not df.empty and len(df) >= 2:
        last_p = float(df['Close'].iloc[-1])
        change = ((last_p / df['Close'].iloc[-2]) - 1) * 100
        weather = "☀️" if change > 0 else "🌧️"
        color = "#00FFA3" if change > 0 else "#FF4B4B"
        
        # Präzision: 5 Stellen für Währungen (=X), sonst 2
        fmt = "{:,.5f}" if "=X" in ticker else "{:,.2f}"
        val_display = fmt.format(last_p)

        with cols[i]:
            st.markdown(f"""
                <div class="market-card">
                    <div style="font-size:0.8rem; color:#8892b0; margin-bottom:4px;">{weather} {TICKER_NAMES.get(ticker, ticker)}</div>
                    <div class="metric-value">{val_display}</div>
                    <div style="color:{color}; font-size:0.85rem; margin-top:4px;">{change:+.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

# SEKTION 2: ANALYSE & NEWS
st.divider()
c_main, c_news = st.columns([2, 1]) # Hauptbereich breiter

with c_main:
    st.subheader("2. Deep-Dive Analyse")
    col_a, col_b = st.columns(2)
    sel_idx = col_a.selectbox("Index:", list(STOCKS_BY_INDEX.keys()))
    sel_stock = col_b.selectbox(
        "Aktie:", 
        STOCKS_BY_INDEX[sel_idx],
        format_func=lambda x: TICKER_NAMES.get(x, x)
    )
    
    data = get_market_data(sel_stock, interval="4h")
    if not data.empty:
        curr_p = float(data['Close'].iloc[-1])
        mom = data['Close'].iloc[-1] - data['Close'].iloc[-14]
        
        # Monte Carlo Plot
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

        # Aktions-Empfehlung
        prob_up = (np.array(sim_ends) > curr_p).mean() * 100
        s_name = TICKER_NAMES.get(sel_stock, sel_stock)
        if mom > 0 and prob_up > 55:
            st.success(f"🟢 **AKTION: KAUFEN** ({s_name} zeigt Aufwärts-Momentum)")
        elif mom < 0 and prob_up < 45:
            st.error(f"🔴 **AKTION: VERKAUFEN** ({s_name} im Abwärtstrend)")
        else:
            st.warning(f"🟡 **AKTION: HALTEN** (Neutrales Umfeld)")

with c_news:
    display_name = TICKER_NAMES.get(sel_stock, sel_stock)
    st.subheader(f"🗞️ {display_name} News")
    news_list = get_stock_news(sel_stock)
    
    if news_list:
        html_news = ""
        for n in news_list:
            link = n.get('link') or n.get('resolvedUrl') or "#"
            # Fallback für Titel
            raw_title = n.get('title') or n.get('summary') or "Link zum Artikel"
            clean_title = (raw_title[:80] + '..') if len(raw_title) > 80 else raw_title
            
            html_news += f'<div class="news-item"><a href="{link}" target="_blank" style="color:#1E90FF; text-decoration:none; font-weight:500;">{clean_title}</a></div>'
        
        st.markdown(f'<div class="news-container"><div class="news-scroll">{html_news}{html_news}</div></div>', unsafe_allow_html=True)
    else:
        st.info(f"Keine aktuellen News für {display_name} gefunden.")
