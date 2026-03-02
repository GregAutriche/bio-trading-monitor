import os
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

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

# Automatischer Refresh alle 45 Sekunden
st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="breakout Strategie")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .ticker-name { color: #00ff00; font-size: 15px; font-weight: bold; margin-bottom: 0px; line-height: 1.2; }
    .open-price { color: #888888; font-size: 11px; margin-top: 2px; }
    .focus-header { color: #00ff00 !important; font-weight: bold; margin-top: 30px; border-bottom: 1px solid #333; padding-bottom: 5px; font-size: 20px; }
    .sig-c { color: #00ff00; font-weight: bold; font-size: 24px; border: 1px solid #00ff00; padding: 2px 10px; border-radius: 5px; }
    .sig-p { color: #ff4b4b; font-weight: bold; font-size: 24px; border: 1px solid #ff4b4b; padding: 2px 10px; border-radius: 5px; }
    .sig-wait { color: #444; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAMENS-DATENBANK (KLARNAMEN) ---
NAME_DB = {
    "EURUSD=X": "Euro / US-Dollar", "^GDAXI": "DAX 40", "^STOXX50E": "EURO STOXX 50", 
    "^IXIC": "NASDAQ 100", "^DJI": "Dow Jones 30", "XU100.IS": "BIST 100",
    "ADS.DE": "Adidas AG", "AIR.DE": "Airbus SE", "ALV.DE": "Allianz SE", "BAS.DE": "BASF SE",
    "BAYN.DE": "Bayer AG", "BEI.DE": "Beiersdorf AG", "BMW.DE": "BMW AG", "CON.DE": "Continental AG",
    "AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.", "AMZN": "Amazon.com", "NVDA": "NVIDIA Corp.",
    "TSLA": "Tesla Inc.", "DIS": "Walt Disney Co.", "V": "Visa Inc.", "MC.PA": "LVMH", "OR.PA": "L'Oréal"
}

@st.cache_data(ttl=86400)
def get_clean_name(ticker):
    if ticker in NAME_DB: return NAME_DB[ticker]
    try:
        info = yf.Ticker(ticker).info
        return info.get('shortName') or info.get('longName') or ticker
    except: return ticker

# --- 3. LOGIK & DATEN-FUNKTIONEN ---
def analyze_bauer(df):
    if df is None or len(df) < 20: return None
    curr = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2]
    prev2 = df['Close'].iloc[-3]
    open_t = df['Open'].iloc[-1]
    
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    
    is_up = (curr > prev) and (prev > prev2)
    is_down = (curr < prev) and (prev < prev2)
    
    signal = "C" if (is_up and curr > sma20) else "P" if (is_down and curr < sma20) else "Wait"
    stop = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0
    delta = ((curr - open_t) / open_t) * 100
    icon = "☀️" if (curr > sma20 and delta > 0.5) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.5 else "⚖️"
    
    return {"price": curr, "open": open_t, "delta": delta, "icon": icon, "signal": signal, "stop": stop}

def get_bauer_data(ticker):
    """Berechnet Daten ohne UI (für Parallelisierung)"""
    try:
        data = yf.Ticker(ticker).history(period="1mo")
        res = analyze_bauer(data)
        if res:
            res['ticker'] = ticker
            res['display_name'] = get_clean_name(ticker)
            return res
    except: return None

def display_bauer_row(res, f_str="{:.2f}"):
    """Rendert die UI-Zeile im Haupt-Thread"""
    cols = st.columns([2.0, 0.6, 1.2, 0.8, 1])
    with cols[0]: st.markdown(f"<div class='ticker-name'>{res['display_name']}</div><div class='open-price'>Start: {f_str.format(res['open'])}</div>", unsafe_allow_html=True)
    with cols[1]: st.markdown(f"<div style='font-size: 1.5rem; margin-top: 5px;'>{res['icon']}</div>", unsafe_allow_html=True)
    with cols[2]:
        c = "#ff4b4b" if res['delta'] < 0 else "#00ff00"
        st.markdown(f"<div style='line-height:1.2;'><small style='color:#888;'>Kurs</small><br><span style='font-size:1.4rem; font-weight:bold;'>{f_str.format(res['price'])}</span><br><small style='color:{c};'>{res['delta']:+.2f}%</small></div>", unsafe_allow_html=True)
    with cols[3]:
        cls = "sig-c" if res['signal'] == "C" else "sig-p" if res['signal'] == "P" else "sig-wait"
        st.markdown(f"<div style='margin-top:15px;'><span class='{cls}'>{res['signal']}</span></div>", unsafe_allow_html=True)
    with cols[4]:
        val = f_str.format(res['stop']) if res['signal'] != "Wait" else "---"
        st.markdown(f"<div style='line-height:1.2;'><small style='color:#888;'>Stop:</small><br><b style='color:#ff4b4b; font-size:1.2rem;'>{val}</b></div>", unsafe_allow_html=True)
    st.divider()

@st.cache_data(ttl=3600)
def get_index_tickers():
    return {
        "DAX": [f"{t}.DE" for t in ["ADS", "AIR", "ALV", "BAS", "BAYN", "BEI", "BMW", "CON", "1COV", "DTG", "DTE", "DBK", "DB1", "EON", "FRE", "FME", "HEI", "HEN3", "IFX", "LIN", "MBG", "MUV2", "PAH3", "PUM", "RWE", "SAP", "SIE", "SHL", "SY1", "VOW3", "VNA"]],
        "NASDAQ 100": ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "PEP", "COST"],
        "EURO STOXX 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA", "SAN.MC", "SIEGn.DE", "ALV.DE", "IBE.MC", "BNP.PA"],
        "DOW JONES 30": ["AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "PG", "TRV", "UNH", "V", "VZ", "WBA", "WMT"]
    }

# --- 4. UI RENDERING ---
st.title("📡 Dr. Gregor Bauer Strategie 📡")
st.write(f"letzes update: {datetime.now().strftime('%H:%M:%S')} | Klarnamen-Check aktiv")

with st.expander("ℹ️ Strategie-Logik & System-Erklärung"):
    st.markdown("""
    **Trend-Check (2-Tage-Regel):** Call (C) bei 2 steigenden Tagen, Put (P) bei 2 fallenden Tagen.  
    **Filter:** Nur Signale in Trendrichtung des SMA 20 (Gleitender Durchschnitt).  
    **Sentiment:** ☀️/🌤️ (Bullisch), ⚖️ (Neutral), ⛈️ (Bärisch).  
    **Stop-Loss:** Dynamisch berechnet mit dem 1.5-fachen der ATR (Volatilität).
    """)

# MAKRO
st.markdown("<p class='focus-header'>🌍 MÄRKTE & FOREX (MACRO) 🌍</p>", unsafe_allow_html=True)
for sym, fmt in [("EURUSD=X", "{:.5f}"), ("^GDAXI", "{:.2f}"), ("^STOXX50E", "{:.2f}"), ("^IXIC", "{:.2f}"), ("XU100.IS", "{:.2f}"), ("^NSEI"),{:.2f}]:
    res = get_bauer_data(sym)
    if res: display_bauer_row(res, fmt)

# SCREENER
st.markdown("<p class='focus-header'>🔭 LIVE SCREENER 🔭</p>", unsafe_allow_html=True)
index_data = get_index_tickers()
idx_choice = st.radio("Index wählen:", list(index_data.keys()), horizontal=True)

if st.button(f"Scan {idx_choice} starten"):
    with st.spinner(f"🚀 Turbo-Scan: Analysiere {idx_choice}..."):
        sorted_tickers = sorted(index_data[idx_choice], key=get_clean_name)
        
        # Parallelisierung nur für Datenabruf
        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(get_bauer_data, sorted_tickers))
        
        # Anzeige im Haupt-Thread (sicher für Streamlit)
        valid_results = [r for r in results if r is not None]
        valid_results.sort(key=lambda x: x['display_name'])
        
        for res in valid_results:
            display_bauer_row(res)




