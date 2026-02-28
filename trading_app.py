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

# Automatischer Refresh alle 45 Sekunden
st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Dr. Bauer Strategie-Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .ticker-name { color: #00ff00; font-size: 15px; font-weight: bold; margin-bottom: 0px; line-height: 1.2; }
    .open-price { color: #888888; font-size: 11px; margin-top: 2px; }
    .method-box { background-color: #111; padding: 15px; border-radius: 5px; border-left: 3px solid #00ff00; font-size: 14px; line-height: 1.6; }
    .focus-header { color: #00ff00 !important; font-weight: bold; margin-top: 30px; border-bottom: 1px solid #333; padding-bottom: 5px; font-size: 20px; }
    .sig-c { color: #00ff00; font-weight: bold; font-size: 24px; border: 1px solid #00ff00; padding: 2px 10px; border-radius: 5px; }
    .sig-p { color: #ff4b4b; font-weight: bold; font-size: 24px; border: 1px solid #ff4b4b; padding: 2px 10px; border-radius: 5px; }
    .sig-wait { color: #444; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK FUNKTIONEN ---
@st.cache_data(ttl=86400)
def get_company_name(ticker_symbol):
    """ Ruft den Klarnamen ab und speichert ihn für 24h im Cache """
    try:
        name = yf.Ticker(ticker_symbol).info.get('longName')
        return name if name else ticker_symbol
    except:
        return ticker_symbol

def analyze_bauer(df):
    """ Kern-Logik: 2-Tage-Trend + SMA Bestätigung """
    if df is None or len(df) < 20: return None
    
    curr = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2]
    prev2 = df['Close'].iloc[-3]
    open_t = df['Open'].iloc[-1]
    
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    
    is_up_trend = (curr > prev) and (prev > prev2)
    is_down_trend = (curr < prev) and (prev < prev2)
    
    signal = "Wait"
    stop_price = 0
    
    if is_up_trend and curr > sma20:
        signal = "C"
        stop_price = curr - (atr * 1.5)
    elif is_down_trend and curr < sma20:
        signal = "P"
        stop_price = curr + (atr * 1.5)
        
    delta = ((curr - open_t) / open_t) * 100
    icon = "☀️" if (curr > sma20 and delta > 0.5) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.5 else "☁️"
    
    return {
        "price": curr, "open": open_t, "delta": delta, "icon": icon,
        "signal": signal, "stop": stop_price
    }

@st.cache_data(ttl=3600)
def get_index_tickers():
    dax = [f"{t}.DE" for t in ["ADS", "AIR", "ALV", "BAS", "BAYN", "BEI", "BMW", "CON", "1COV", "DTG", "DTE", "DBK", "DB1", "EON", "FRE", "FME", "HEI", "HEN3", "IFX", "LIN", "MBG", "MUV2", "PAH3", "PUM", "RWE", "SAP", "SIE", "SHL", "SY1", "VOW3", "VNA"]]
    ndx = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "PEP", "COST"]
    return {"DAX": dax, "NASDAQ 100": ndx}

def render_bauer_row(label, ticker, f_str="{:.2f}"):
    try:
        # 1. Namen abrufen (Klarname statt Symbol)
        display_name = get_company_name(ticker)
        
        # 2. Daten laden
        data = yf.Ticker(ticker).history(period="1mo")
        res = analyze_bauer(data)
        
        if res:
            cols = st.columns([2.0, 0.6, 1.2, 0.8, 1])
            
            with cols[0]: # KLARNAME & START
                st.markdown(f"<div class='ticker-name'>{display_name}</div><div class='open-price'>Start: {f_str.format(res['open'])}</div>", unsafe_allow_html=True)
            
            with cols[1]: # WETTER
                st.markdown(f"<div style='font-size: 1.5rem; margin-top: 5px;'>{res['icon']}</div>", unsafe_allow_html=True)
            
            with cols[2]: # KURS (Gleiche Größe wie Signal/Name)
                delta_color = "#ff4b4b" if res['delta'] < 0 else "#00ff00"
                st.markdown(f"""
                    <div style='line-height: 1.2;'>
                        <small style='color: #888;'>Kurs</small><br>
                        <span style='font-size: 1.4rem; font-weight: bold;'>{f_str.format(res['price'])}</span><br>
                        <small style='color: {delta_color};'>{res['delta']:+.2f}%</small>
                    </div>
                """, unsafe_allow_html=True)
            
            with cols[3]: # SIGNAL (C / P / Wait)
                sig_class = "sig-c" if res['signal'] == "C" else "sig-p" if res['signal'] == "P" else "sig-wait"
                st.markdown(f"<div style='margin-top: 15px;'><span class='{sig_class}'>{res['signal']}</span></div>", unsafe_allow_html=True)
            
            with cols[4]: # STOP
                val = f_str.format(res['stop']) if res['signal'] != "Wait" else "---"
                st.markdown(f"<div style='line-height: 1.2;'><small style='color: #888;'>Stop:</small><br><b style='color:#ff4b4b; font-size: 1.2rem;'>{val}</b></div>", unsafe_allow_html=True)
            
            st.divider()
    except Exception as e:
        pass

# --- 3. UI RENDERING ---
st.title("📡 Dr. Bauer Strategie-Terminal")
st.write(f"Refreshed: {datetime.now().strftime('%H:%M:%S')} | Modus: Klarnamen-Anzeige")

with st.expander("📖 STRATEGIE-DETAILS"):
    st.markdown("<div class='method-box'>Anzeige von <b>Klarnamen</b> via Yahoo Finance API. Signale basieren auf 2-Tage-Trend-Bestätigung.</div>", unsafe_allow_html=True)

# MÄRKTE SEKTION
st.markdown("<p class='focus-header'>🌍 MÄRKTE & FOREX (MACRO) 🌍</p>", unsafe_allow_html=True)
macro_symbols = {
    "Euro / US-Dollar": ("EURUSD=X", "{:.5f}"),
    "Euro / Russischer Rubel": ("EURRUB=X", "{:.4f}"),
    "EURO STOXX 50": ("^STOXX50E", "{:.2f}"),
    "NASDAQ 100 Index": ("^IXIC", "{:.2f}"),
    "Borsa Istanbul 100": ("XU100.IS", "{:.2f}"),
    "MOEX Russia Index": ("IMOEX.ME", "{:.2f}")
}
for label, (sym, fmt) in macro_symbols.items():
    render_bauer_row(label, sym, fmt)

# SCREENER SEKTION
st.markdown("<p class='focus-header'>🔭 LIVE SCREENER 🔭</p>", unsafe_allow_html=True)
index_data = get_index_tickers()
idx_choice = st.radio("Index wählen:", list(index_data.keys()), horizontal=True)

if st.button(f"Scan {idx_choice} starten"):
    with st.spinner("Lade Unternehmensnamen und analysiere Kurse..."):
        for t in index_data[idx_choice]:
            render_bauer_row(t, t)
