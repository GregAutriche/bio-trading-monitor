import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📈")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    h1, h2, h3, p, span, label, div { color: #c9d1d9 !important; font-family: 'Segoe UI', sans-serif; }
    .sig-c { color: #3fb950; font-weight: bold; border: 1px solid #3fb950; padding: 3px 10px; border-radius: 5px; background: rgba(63, 185, 80, 0.1); }
    .sig-p { color: #f85149; font-weight: bold; border: 1px solid #f85149; padding: 3px 10px; border-radius: 5px; background: rgba(248, 81, 73, 0.1); }
    .sig-wait { color: #8b949e; font-size: 0.9rem; border: 1px solid #30363d; padding: 3px 10px; border-radius: 5px; }
    .focus-header { color: #f0883e !important; font-weight: bold; border-bottom: 1px solid #30363d; padding-bottom: 5px; margin: 25px 0 15px 0; }
    .metric-box { background: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK: DATENREINIGUNG & BACKTEST ---
def clean_df(df):
    """ Bereinigt Yahoo Finance Multi-Index Spalten für 2026 """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def calculate_probability(df, signal_type):
    """ Historischer Check der letzten 250 Tage """
    if df is None or len(df) < 50: return 50.0
    bt_df = df.copy()
    bt_df['SMA20'] = bt_df['Close'].rolling(window=20).mean()
    
    hits, signals = 0, 0
    for i in range(20, len(bt_df) - 5):
        c, p, p2 = bt_df['Close'].iloc[i], bt_df['Close'].iloc[i-1], bt_df['Close'].iloc[i-2]
        sma = bt_df['SMA20'].iloc[i]
        
        h_sig = "C" if (c > p > p2 and c > sma) else "P" if (c < p < p2 and c < sma) else None
        if h_sig == signal_type:
            signals += 1
            if (signal_type == "C" and bt_df['Close'].iloc[i+3] > c) or \
               (signal_type == "P" and bt_df['Close'].iloc[i+3] < c):
                hits += 1
    return (hits / signals * 100) if signals > 0 else 50.0

# --- 3. KERN-ANALYSE ---
def analyze_ticker(ticker):
    try:
        # Download mit Fehler-Toleranz
        df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 25: return None
        df = clean_df(df)
        
        # Aktuelle Daten
        curr, prev, prev2 = df['Close'].iloc[-1], df['Close'].iloc[-2], df['Close'].iloc[-3]
        open_t = df['Open'].iloc[-1]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        
        # Bauer Signal
        signal = "Wait"
        if (curr > prev > prev2) and curr > sma20: signal = "C"
        elif (curr < prev < prev2) and curr < sma20: signal = "P"
        
        prob = calculate_probability(df, signal) if signal != "Wait" else 0
        delta = ((curr - open_t) / open_t) * 100
        stop = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0
        
        return {"ticker": ticker, "price": float(curr), "delta": float(delta), 
                "signal": signal, "stop": float(stop), "prob": float(prob)}
    except: return None

# --- 4. UI KOMPONENTEN ---
def render_row(res, is_forex=False):
    fmt = "{:.5f}" if is_forex else "{:.2f}"
    with st.container():
        c1, c2, c3, c4, c5 = st.columns([1.5, 1, 1, 1, 2])
        c1.markdown(f"**{res['ticker']}**<br><small>Preis: {fmt.format(res['price'])}</small>", unsafe_allow_html=True)
        
        color = "#3fb950" if res['delta'] >= 0 else "#f85149"
        c2.markdown(f"<br><span style='color:{color}'>{res['delta']:+.2f}%</span>", unsafe_allow_html=True)
        
        s_cls = "sig-c" if res['signal'] == "C" else "sig-p" if res['signal'] == "P" else "sig-wait"
        c3.markdown(f"<br><span class='{s_cls}'>{res['signal']}</span>", unsafe_allow_html=True)
        
        sl = fmt.format(res['stop']) if res['signal'] != "Wait" else "---"
        c4.markdown(f"<small>Stop-Loss</small><br><code>{sl}</code>", unsafe_allow_html=True)
        
        if res['signal'] != "Wait":
            p_col = "#3fb950" if res['prob'] > 55 else "#f0883e"
            c5.markdown(f"<small>Wahrscheinlichkeit: {res['prob']:.1f}%</small>", unsafe_allow_html=True)
            c5.progress(int(res['prob']))
        else:
            c5.markdown("<br><small style='color:#484f58'>Kein Setup</small>", unsafe_allow_html=True)
        st.divider()

# --- 5. MAIN APP ---
st.title("📡 Dr. Gregor Bauer: Multi-Asset Screener 2026")
st.caption(f"Letzter Sync: {datetime.now().strftime('%H:%M:%S')} (Yahoo Finance API v2026)")

# --- SEKTION 1: INDIZES & FOREX ---
st.markdown("<h3 class='focus-header'>🌍 Global Macro & Währungen</h3>", unsafe_allow_html=True)
macro_tickers = ["^GDAXI", "^IXIC", "^STOXX50E", "EURUSD=X", "USDJPY=X", "BTC-USD"]

with ThreadPoolExecutor(max_workers=10) as executor:
    macros = list(executor.map(analyze_ticker, macro_tickers))
    for r in filter(None, macros):
        render_row(r, is_forex=("USD" in r['ticker'] or "=" in r['ticker']))

# --- SEKTION 2: LIVE SCREENER ---
st.markdown("<h3 class='focus-header'>🔭 Stock Screener (DAX & Tech)</h3>", unsafe_allow_html=True)
index_map = {
    "DAX 40": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "DBK.DE", "DTE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "NASDAQ 100": ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "AVGO", "COST", "NFLX"]
}
choice = st.selectbox("Wähle Marktsegment:", list(index_map.keys()))

if st.button(f"🔍 Scan {choice} jetzt starten"):
    with st.spinner(f"Analysiere {len(index_map[choice])} Ticker mit Backtest-Engine..."):
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(analyze_ticker, index_map[choice]))
            
            # Sortierung: Signale mit höchster Wahrscheinlichkeit zuerst
            sorted_res = sorted([r for r in results if r], 
                                key=lambda x: (x['signal'] == "Wait", -x['prob']))
            
            if not sorted_res:
                st.warning("Keine Daten empfangen. Bitte yfinance updaten.")
            else:
                for r in sorted_res:
                    render_row(r)

st.sidebar.info("Strategie: 2-Tage Trendbestätigung + SMA 20 Filter. Stop-Loss basiert auf 1.5x ATR.")
