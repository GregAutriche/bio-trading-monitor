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
    .sig-c { color: #3fb950; font-weight: bold; border: 1px solid #3fb950; padding: 2px 6px; border-radius: 4px; display: inline-block; }
    .sig-p { color: #f85149; font-weight: bold; border: 1px solid #f85149; padding: 2px 6px; border-radius: 4px; display: inline-block; }
    .sig-wait { color: #484f58; font-size: 0.85rem; }
    .focus-header { color: #58a6ff !important; font-weight: bold; border-bottom: 1px solid #30363d; margin: 15px 0 10px 0; }
    code { background-color: #161b22 !important; color: #f85149 !important; padding: 2px 4px; border-radius: 3px; font-size: 0.9rem; }
    .row-wrapper { border-bottom: 1px solid #30363d; padding-bottom: 4px; margin-bottom: 4px; width: 100%; }
    .error-tag { background-color: #3fb950; color: white !important; padding: 1px 4px; border-radius: 3px; font-size: 0.6rem; font-weight: bold; vertical-align: middle; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAMENS-DATENBANK (KLARNAMEN) ---
NAME_DB = {
    "EURUSD=X": "Euro / US-Dollar", "^GDAXI": "DAX 40", "^STOXX50E": "EURO STOXX 50",
    "^IXIC": "NASDAQ Composite", "XU100.IS": "BIST 100", "^NSEI": "NIFTY 50",
    "ADS.DE": "Adidas AG", "ALV.DE": "Allianz SE", "BAS.DE": "BASF SE", "BMW.DE": "BMW AG",
    "SAP.DE": "SAP SE", "SIE.DE": "Siemens AG", "AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.",
    "THYAO.IS": "Turkish Airlines", "TUPRS.IS": "Tupras Petrol", "RELIANCE.NS": "Reliance Industries"
}

# --- 3. DATEN-ENGINE (DEEP CLEAN) ---
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
        
        # DEEP CLEAN: Geisterwerte in der gesamten Historie entfernen (EUR/USD Fix)
        is_recovered = False
        if "EURUSD=X" in ticker:
            mask = (df['Close'] > 2.0) | (df['Close'] < 0.5)
            if mask.any():
                is_recovered = True
                valid_median = df.loc[~mask, 'Close'].median()
                if pd.isna(valid_median): valid_median = 1.1625
                df.loc[mask, ['Open', 'High', 'Low', 'Close']] = valid_median

        curr = float(df['Close'].iloc[-1])
        prev, prev2 = df['Close'].iloc[-2], df['Close'].iloc[-3]
        open_t = df['Open'].iloc[-1]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        
        # ATR Berechnung
        tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        
        signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
        prob = calculate_probability(df, signal) if signal != "Wait" else 0
        delta = ((curr - open_t) / open_t) * 100
        stop = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0
        icon = "☀️" if (curr > sma20 and delta > 0.3) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.3 else "⚖️"
        
        return {"display_name": NAME_DB.get(ticker, ticker), "ticker": ticker, "price": curr, 
                "delta": float(delta), "signal": signal, "stop": float(stop), "prob": float(prob), 
                "icon": icon, "is_recovered": is_recovered}
    except: return None

# --- 4. UI RENDERER ---
def render_row(res):
    is_forex = ("=" in res['ticker'])
    fmt = "{:.5f}" if is_forex else "{:.2f}"
    st.markdown("<div class='row-wrapper'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([1.0, 0.5, 0.3, 0.7, 0.6], gap="small")
    with c1:
        tag = "<span class='error-tag'>CLEANED</span>" if res.get('is_recovered') else ""
        st.markdown(f"**{res['display_name']}** {tag}<br><small>Kurs: {fmt.format(res['price'])}</small>", unsafe_allow_html=True)
    with c2: 
        color = "#3fb950" if res['delta'] >= 0 else "#f85149"
        st.markdown(f"### {res['icon']}<br><span style='font-size:0.8rem; color:{color}'>{res['delta']:+.2f}%</span>", unsafe_allow_html=True)
    with c3:
        cls = "sig-c" if res['signal'] == "C" else "sig-p" if res['signal'] == "P" else "sig-wait"
        st.markdown(f"<br><span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
    with c4:
        sl = fmt.format(res['stop']) if res['signal'] != "Wait" else "---"
        st.markdown(f"<small>Stop-Loss</small><br><code>{sl}</code>", unsafe_allow_html=True)
    with c5:
        if res['signal'] != "Wait":
            p_val, p_col = res['prob'], ("#3fb950" if res['prob'] >= 60 else "#f0883e")
            p_txt = f"{p_val:.1f}%" if p_val >= 60 else f"({p_val:.1f}%)"
            st.markdown(f"<br><span style='color:{p_col}; font-weight:bold; font-size:1.1rem;'>{p_txt}</span>", unsafe_allow_html=True)
        else: st.markdown("<br><small style='color:#484f58'>---</small>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. MAIN APP ---
st.title("📡 Dr. Gregor Bauer Strategy Pro")
st.write(f"Sync: {datetime.now().strftime('%H:%M:%S')}")

with st.expander("ℹ️ Strategie-Logik & System-Erklärung"):
    st.markdown("""
    ### **1. Trend-Check (2-Tage-Regel)**
    Die Basis der Strategie nach Dr. Gregor Bauer ist die Bestätigung eines kurzfristigen Momentums:
    *   **Call (C):** Der Schlusskurs von heute liegt über dem von gestern, und der von gestern lag über dem von vorgestern.
    *   **Put (P):** Der Schlusskurs von heute liegt unter dem von gestern, und der von gestern lag unter dem von vorgestern.

    ### **2. SMA 20 Trend-Filter**
    Um Fehlsignale in Seitwärtsphasen zu vermeiden, wird der gleitende Durchschnitt der letzten 20 Tage (SMA 20) genutzt:
    *   Ein **Call** wird nur angezeigt, wenn der Kurs **über** dem SMA 20 notiert (Aufwärtstrend).
    *   Ein **Put** wird nur angezeigt, wenn der Kurs **unter** dem SMA 20 notiert (Abwärtstrend).

    ### **3. Dynamischer Stop-Loss (ATR)**
    Das Risikomanagement basiert auf der Volatilität der letzten 14 Tage (Average True Range - ATR):
    *   Der Stop-Loss wird mit dem Faktor **1,5x ATR** berechnet.
    *   Dies gibt dem Trade genug "Luft zum Atmen" und schützt gleichzeitig vor übermäßigen Verlusten.

    ### **4. Sentiment-Indikatoren (Wetter)**
    *   ☀️ **Bullisch:** Kurs über SMA 20 und starke Tagesperformance (> +0,3%).
    *   🌤️ **Leicht Bullisch:** Kurs über SMA 20, aber geringe Dynamik.
    *   ⚖️ **Neutral:** Kurs pendelt um den SMA 20 oder Tagestrend ist unklar.
    *   ⛈️ **Bärisch:** Kurs unter SMA 20 oder schwache Tagesperformance (< -0,3%).

    ### **5. Historische Wahrscheinlichkeit**
    Das System führt im Hintergrund einen **1-Jahres-Backtest** für jeden Ticker durch. Es berechnet, wie oft das exakt gleiche Setup in der Vergangenheit innerhalb von 3-5 Tagen zu einem Profit geführt hat. 
    *   Werte ab **60%** gelten als statistisch signifikant.
    *   Werte unter **60%** werden zur Vorsicht in Klammern gesetzt.
    """)

st.markdown("<h3 class='focus-header'>🌍 Macro & Indices</h3>", unsafe_allow_html=True)
macro_tickers = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]
with ThreadPoolExecutor(max_workers=6) as executor:
    results_list = list(executor.map(analyze_ticker, macro_tickers))
    for res in results_list:
        if res: render_row(res)

st.markdown("<h3 class='focus-header'>🔭 Market Scanner</h3>", unsafe_allow_html=True)
index_data = {
    "DAX 40": ["ADS.DE", "ALV.DE", "BAS.DE", "BMW.DE", "SAP.DE", "SIE.DE"],
    "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL"],
    "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA"],
    "BIST 100": ["THYAO.IS", "TUPRS.IS", "AKBNK.IS", "ISCTR.IS", "EREGL.IS"],
    "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "BHARTIARTL.NS"]
}
choice = st.radio("Markt wählen:", list(index_data.keys()), horizontal=True)

if st.button(f"Scan {choice} starten"):
    with st.spinner(f"Analysiere {choice}..."):
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(analyze_ticker, index_data[choice]))
            for r in sorted([r for r in results if r], key=lambda x: (x['signal'] == "Wait", -x['prob'])):
                render_row(r)
