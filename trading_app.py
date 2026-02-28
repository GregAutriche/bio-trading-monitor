import os
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 0. SETUP & AUTO-INSTALL ---
try:
    import lxml
except ImportError:
    os.system('pip install lxml')

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

# 45 Sekunden Intervall
st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Dr. Bauer Strategie-Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .ticker-name { color: #00ff00; font-size: 16px; font-weight: bold; margin-bottom: 0px; }
    .open-price { color: #888888; font-size: 11px; margin-top: -5px; }
    .method-box { background-color: #111; padding: 15px; border-radius: 5px; border-left: 3px solid #00ff00; font-size: 14px; line-height: 1.6; }
    .focus-header { color: #00ff00 !important; font-weight: bold; margin-top: 30px; border-bottom: 1px solid #333; padding-bottom: 5px; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK FUNKTIONEN ---
def analyze_bauer(df):
    if df is None or len(df) < 20: return None
    curr = df['Close'].iloc[-1]
    open_t = df['Open'].iloc[-1]
    prev_high = df['High'].iloc[-2]
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    delta = ((curr - open_t) / open_t) * 100
    
    upper_wick = df['High'].iloc[-1] - max(curr, open_t)
    is_strong = upper_wick < (abs(curr - open_t) * 0.35)
    
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    icon = "☀️" if (curr > sma20 and delta > 0.5) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.5 else "☁️"
    
    return {
        "price": curr, "open": open_t, "delta": delta, "icon": icon,
        "signal": (curr > prev_high) and is_strong and (curr > sma20),
        "stop": curr - (atr * 1.5)
    }

@st.cache_data(ttl=3600)
def get_index_tickers():
    try:
        # Fallback Listen falls Wiki-Scraping hakt
        dax = [f"{t}.DE" for t in ["ADS", "AIR", "ALV", "BAS", "BAYN", "BEI", "BMW", "CON", "1COV", "DTG", "DTE", "DBK", "DB1", "EON", "FRE", "FME", "HEI", "HEN3", "IFX", "LIN", "MBG", "MUV2", "PAH3", "PUM", "RWE", "SAP", "SIE", "SHL", "SY1", "VOW3", "VNA"]]
        ndx = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "PEP", "COST"]
        return {"DAX": dax, "NASDAQ 100": ndx}
    except:
        return {"FOKUS": ["AAPL", "NVDA", "SAP.DE"]}

def render_bauer_row(label, ticker, f_str="{:.2f}"):
    try:
        data = yf.Ticker(ticker).history(period="1mo")
        res = analyze_bauer(data)
        if res:
            cols = st.columns([1.5, 0.8, 1.2, 0.8, 1])
            with cols[0]: st.markdown(f"<div class='ticker-name'>{label}</div><div class='open-price'>Start: {f_str.format(res['open'])}</div>", unsafe_allow_html=True)
            with cols[1]: st.markdown(f"## {res['icon']}")
            with cols[2]: st.metric("Kurs", f_str.format(res['price']), f"{res['delta']:+.2f}%")
            with cols[3]: st.markdown(f"## {'🚀' if res['signal'] else 'Wait'}")
            with cols[4]: st.markdown(f"<small>Stop:</small><br><b style='color:#ff4b4b;'>{f_str.format(res['stop'])}</b>", unsafe_allow_html=True)
            st.divider()
    except: pass

# --- 3. UI RENDERING ---
st.title("📡 Dr. Bauer Strategie-Terminal")
st.write(f"Refreshed: {datetime.now().strftime('%H:%M:%S')} | 45s Update")

with st.expander("📖 AUSFÜHRLICHE BESCHREIBUNG DER STRATEGIE-LOGIK"):
    st.markdown("""<div class='method-box'><b>1. Börsen-Wetter:</b> Trend via SMA 20. ☀️ bei Kurs > SMA 20.<br><b>2. Candlestick:</b> Signal nur bei Schluss im oberen Drittel.<br><b>3. Breakout:</b> 🚀 bei Kurs > gestrigem Hoch + Trend.<br><b>4. Vola-Stop:</b> 1.5 * ATR Puffer.</div>""", unsafe_allow_html=True)

# --- MACRO SEKTION ---
st.markdown("<p class='focus-header'>🌍 MÄRKTE & FOREX (MACRO) 🌍</p>", unsafe_allow_html=True)
macro_symbols = {
    "EUR/USD": ("EURUSD=X", "{:.5f}"),
    "EUR/RUB": ("EURRUB=X", "{:.4f}"),
    "EUROSTOXX 50": ("^STOXX50E", "{:.2f}"),
    "NASDAQ 100": ("^IXIC", "{:.2f}"),
    "BIST 100 (TR)": ("XU100.IS", "{:.2f}"),
    "NIFTY 500 (IN)": ("^CRSLDX", "{:.2f}"),
    "MOEX RUSSIA": ("IMOEX.ME", "{:.2f}")
}

for label, (sym, fmt) in macro_symbols.items():
    render_bauer_row(label, sym, fmt)

# --- SCREENER SEKTION ---
st.markdown("<p class='focus-header'>🔭 LIVE SCREENER 🔭</p>", unsafe_allow_html=True)
index_data = get_index_tickers()
idx_choice = st.radio("Index wählen:", list(index_data.keys()), horizontal=True)

if st.button(f"Scan {idx_choice} starten"):
    with st.spinner("Analysiere Einzelwerte..."):
        for t in index_data[idx_choice]:
            render_bauer_row(t, t)
