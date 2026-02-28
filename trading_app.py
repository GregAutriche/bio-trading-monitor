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

# 45 Sekunden Intervall für den Auto-Refresh
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
    .signal-c { color: #00ff00; font-weight: bold; font-size: 24px; }
    .signal-p { color: #ff4b4b; font-weight: bold; font-size: 24px; }
    .signal-wait { color: #555555; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK FUNKTIONEN ---
def analyze_bauer(df):
    # Wir benötigen mind. 3 Tage für den 2-Tage-Trend-Check (Heute, Gestern, Vorgestern)
    if df is None or len(df) < 20: return None
    
    # Preise extrahieren
    curr = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2]
    prev2 = df['Close'].iloc[-3]
    open_t = df['Open'].iloc[-1]
    
    # Gleitender Durchschnitt (SMA 20)
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    
    # Volatilität (ATR) für den Stop Loss
    df['TR'] = pd.concat([
        df['High'] - df['Low'], 
        abs(df['High'] - df['Close'].shift()), 
        abs(df['Low'] - df['Close'].shift())
    ], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    
    # 1. TREND-LOGIK (2-Tage Bestätigung)
    # C (Call): Kurs steigt 2 Tage in Folge
    is_up_trend = (curr > prev) and (prev > prev2)
    # P (Put): Kurs fällt 2 Tage in Folge
    is_down_trend = (curr < prev) and (prev < prev2)
    
    # 2. SIGNAL-GENERIERUNG
    # Ein Signal erfolgt nur, wenn der Trend zur Lage zum SMA passt
    if is_up_trend and curr > sma20:
        signal = "C"
        stop_price = curr - (atr * 1.5)
    elif is_down_trend and curr < sma20:
        signal = "P"
        stop_price = curr + (atr * 1.5)
    else:
        signal = "Wait"
        stop_price = 0
        
    # 3. WETTER-ICON (Bauer-Standard)
    delta = ((curr - open_t) / open_t) * 100
    icon = "☀️" if (curr > sma20 and delta > 0.5) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.5 else "☁️"
    
    return {
        "price": curr, "open": open_t, "delta": delta, "icon": icon,
        "signal": signal, "stop": stop_price
    }

@st.cache_data(ttl=3600)
def get_index_tickers():
    # DAX und NASDAQ 100 Auswahl
    dax = [f"{t}.DE" for t in ["ADS", "AIR", "ALV", "BAS", "BAYN", "BEI", "BMW", "CON", "1COV", "DTG", "DTE", "DBK", "DB1", "EON", "FRE", "FME", "HEI", "HEN3", "IFX", "LIN", "MBG", "MUV2", "PAH3", "PUM", "RWE", "SAP", "SIE", "SHL", "SY1", "VOW3", "VNA"]]
    ndx = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "PEP", "COST"]
    return {"DAX": dax, "NASDAQ 100": ndx}

def render_bauer_row(label, ticker, f_str="{:.2f}"):
    try:
        data = yf.Ticker(ticker).history(period="1mo")
        res = analyze_bauer(data)
        if res:
            cols = st.columns([1.5, 0.8, 1.2, 0.8, 1])
            
            with cols[0]: 
                st.markdown(f"<div class='ticker-name'>{label}</div><div class='open-price'>Start: {f_str.format(res['open'])}</div>", unsafe_allow_html=True)
            
            with cols[1]: 
                st.markdown(f"## {res['icon']}")
            
            with cols[2]: 
                st.metric("Kurs", f_str.format(res['price']), f"{res['delta']:+.2f}%")
            
            with cols[3]: 
                # Visuelle Aufbereitung von C / P / Wait
                if res['signal'] == "C":
                    st.markdown("<span class='signal-c'>C</span>", unsafe_allow_html=True)
                elif res['signal'] == "P":
                    st.markdown("<span class='signal-p'>P</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='signal-wait'>Wait</span>", unsafe_allow_html=True)
            
            with cols[4]: 
                if res['signal'] != "Wait":
                    st.markdown(f"<small>Stop:</small><br><b style='color:#ff4b4b;'>{f_str.format(res['stop'])}</b>", unsafe_allow_html=True)
                else:
                    st.markdown("<small>Stop:</small><br>---", unsafe_allow_html=True)
            
            st.divider()
    except:
        pass

# --- 3. UI RENDERING ---
st.title("📡 Dr. Bauer Strategie-Terminal")
st.write(f"Refreshed: {datetime.now().strftime('%H:%M:%S')} | 45s Update")

# --- EXPANDER METHODIK ---
with st.expander("📖 STRATEGIE-LOGIK: TRENDBESTÄTIGUNG (C/P)"):
    st.markdown("""
    <div class='method-box'>
        <b>Kaufempfehlungen basierend auf 2-Tage-Trend:</b><br>
        <ul>
            <li><b>C (Call):</b> Erscheint, wenn der Kurs 2 Tage in Folge gestiegen ist (Heute > Gestern > Vorgestern) UND über dem SMA 20 liegt.</li>
            <li><b>P (Put):</b> Erscheint, wenn der Kurs 2 Tage in Folge gefallen ist (Heute < Gestern < Vorgestern) UND unter dem SMA 20 liegt.</li>
            <li><b>Wait:</b> Kein klarer Trend über 2 Tage oder Widerspruch zum SMA 20.</li>
            <li><b>Stop-Loss:</b> Basierend auf 1.5x ATR (Average True Range).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

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
