import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    h1, h2, h3, p, span, label, div { color: #c9d1d9 !important; font-family: 'Courier New', monospace; }
    .sig-c { color: #3fb950; font-weight: bold; border: 1px solid #3fb950; padding: 2px 8px; border-radius: 4px; }
    .sig-p { color: #f85149; font-weight: bold; border: 1px solid #f85149; padding: 2px 8px; border-radius: 4px; }
    .sig-wait { color: #484f58; font-size: 0.9rem; }
    .focus-header { color: #58a6ff !important; font-weight: bold; border-bottom: 1px solid #30363d; margin: 20px 0; }
    code { background-color: #161b22 !important; color: #f85149 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAMENS-DATENBANK (KLARNAMEN) ---
NAME_DB = {
    "EURUSD=X": "Euro / US-Dollar",
    "^GDAXI": "DAX 40", 
    "^STOXX50E": "EURO STOXX 50",
    "^IXIC": "NASDAQ Composite", 
    "^DJI": "Dow Jones 30", 
    "XU100.IS": "BIST 100", 
    "^NSEI": "NIFTY 50",
    # Aktien Klarnamen
    "ADS.DE": "Adidas AG", "ALV.DE": "Allianz SE", "BAS.DE": "BASF SE", "BMW.DE": "BMW AG",
    "SAP.DE": "SAP SE", "SIE.DE": "Siemens AG", "AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.",
    "NVDA": "NVIDIA Corp.", "AMZN": "Amazon.com", "TSLA": "Tesla Inc.", "GOOGL": "Alphabet Inc.",
    "THYAO.IS": "Turkish Airlines", "TUPRS.IS": "Tupras Petrol", "RELIANCE.NS": "Reliance Industries"
}

# --- 3. DATEN-ENGINE ---
def clean_df(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def calculate_probability(df, signal_type):
    if df is None or len(df) < 50: return 50.0
    bt_df = df.copy()
    bt_df['SMA20'] = bt_df['Close'].rolling(window=20).mean()
    hits, signals = 0, 0
    for i in range(25, len(bt_df) - 5):
        c, p, p2 = bt_df['Close'].iloc[i], bt_df['Close'].iloc[i-1], bt_df['Close'].iloc[i-2]
        sma = bt_df['SMA20'].iloc[i]
        h_sig = "C" if (c > p > p2 and c > sma) else "P" if (c < p < p2 and c < sma) else None
        if h_sig == signal_type:
            signals += 1
            if (signal_type == "C" and bt_df['Close'].iloc[i+3] > c) or \
               (signal_type == "P" and bt_df['Close'].iloc[i+3] < c):
                hits += 1
    return (hits / signals * 100) if signals > 0 else 50.0

def analyze_ticker(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 25: return None
        df = clean_df(df)
        curr, prev, prev2 = df['Close'].iloc[-1], df['Close'].iloc[-2], df['Close'].iloc[-3]
        open_t = df['Open'].iloc[-1]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        
        signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
        prob = calculate_probability(df, signal) if signal != "Wait" else 0
        delta = ((curr - open_t) / open_t) * 100
        stop = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0
        icon = "☀️" if (curr > sma20 and delta > 0.3) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.3 else "⚖️"
        
        return {"display_name": NAME_DB.get(ticker, ticker), "ticker": ticker, "price": float(curr), 
                "delta": float(delta), "signal": signal, "stop": float(stop), "prob": float(prob), "icon": icon}
    except: return None

# --- 4. UI KOMPONENTE ---
def render_row(res):
    is_forex = ("=" in res['ticker'])
    fmt = "{:.5f}" if is_forex else "{:.2f}"
    with st.container():
        c1, c2, c3, c4, c5 = st.columns([1.5, 0.8, 1, 1, 1.2])
        # Anzeige NUR Klarnamen
        c1.markdown(f"**{res['display_name']}**<br><small>Kurs: {fmt.format(res['price'])}</small>", unsafe_allow_html=True)
        color = "#3fb950" if res['delta'] >= 0 else "#f85149"
        c2.markdown(f"### {res['icon']}<br><span style='font-size:0.8rem; color:{color}'>{res['delta']:+.2f}%</span>", unsafe_allow_html=True)
        s_cls = "sig-c" if res['signal'] == "C" else "sig-p" if res['signal'] == "P" else "sig-wait"
        c3.markdown(f"<br><span class='{s_cls}'>{res['signal']}</span>", unsafe_allow_html=True)
        sl = fmt.format(res['stop']) if res['signal'] != "Wait" else "---"
        c4.markdown(f"<small>Stop-Loss</small><br><code>{sl}</code>", unsafe_allow_html=True)
        if res['signal'] != "Wait":
            p_col = "#3fb950" if res['prob'] > 55 else "#f0883e"
            c5.markdown(f"<br><span style='color:{p_col}; font-weight:bold; font-size:1.2rem;'>{res['prob']:.1f}%</span>", unsafe_allow_html=True)
        else:
            c5.markdown("<br><small style='color:#484f58'>---</small>", unsafe_allow_html=True)
        st.divider()

# --- 5. MAIN APP ---
st.title("📡 Dr. Gregor Bauer Strategy Screener")
st.write(f"Stand: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

# MACRO REIHENFOLGE: EUR/USD -> DAX -> EURO STOXX -> NASDAQ -> BIST -> NIFTY
st.markdown("<h3 class='focus-header'>🌍 Global Macro & Indices</h3>", unsafe_allow_html=True)
macro_tickers = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]

with ThreadPoolExecutor(max_workers=6) as executor:
    # Die Ergebnisse in der Reihenfolge von macro_tickers halten
    results_dict = {r['ticker']: r for r in filter(None, executor.map(analyze_ticker, macro_tickers))}
    for t in macro_tickers:
        if t in results_dict:
            render_row(results_dict[t])

st.markdown("<h3 class='focus-header'>🔭 Market Scanner</h3>", unsafe_allow_html=True)
index_data = {
    "DAX 40": ["ADS.DE", "ALV.DE", "BAS.DE", "BMW.DE", "SAP.DE", "SIE.DE"],
    "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL"],
    "BIST 100": ["THYAO.IS", "TUPRS.IS", "AKBNK.IS", "ISCTR.IS", "EREGL.IS"],
    "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "BHARTIARTL.NS"]
}
choice = st.radio("Markt wählen:", list(index_data.keys()), horizontal=True)

if st.button(f"Scan {choice} starten"):
    with st.spinner("Analysiere..."):
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(analyze_ticker, index_data[choice]))
            sorted_res = sorted([r for r in results if r], key=lambda x: (x['signal'] == "Wait", -x['prob']))
            for r in sorted_res:
                render_row(r)
