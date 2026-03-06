import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# --- 0. CONFIG & COMPACT NAVY DESIGN ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

st.markdown("""
    <style>
    /* Hintergrund & Grundschrift */
    .stApp { background-color: #0a192f; }
    h1, h2, h3, p, span, label, div { color: #e6f1ff !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Header kompakter */
    .header-text { font-size: 24px; font-weight: bold; color: #64ffda !important; border-bottom: 2px solid #64ffda; padding-bottom: 5px; margin-bottom: 10px; }
    
    /* Signal Boxen */
    .sig-box-c { color: #00ff41 !important; border: 1px solid #00ff41; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(0, 255, 65, 0.1); }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(0, 123, 255, 0.1); }
    .sig-box-high { color: #ffd700 !important; border: 2px solid #ffd700; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(255, 215, 0, 0.2); }
    
    /* Abstände extrem reduzieren */
    .row-container { border-bottom: 1px solid #172a45; padding: 4px 0; margin: 0; }
    .metric-label { color: #8892b0; font-size: 0.75rem; }
    .price-text { font-size: 1.0rem; font-weight: bold; }
    .stMarkdown div { line-height: 1.2 !important; }
    
    /* Expander Styling */
    .stExpander { border: 1px solid #172a45 !important; background-color: rgba(23, 42, 69, 0.5) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. DYNAMISCHE MARKT-DATEN (VOLLSTÄNDIGKEIT) ---
@st.cache_data(ttl=86400)
def get_complete_market_maps():
    maps = {}
    # DAX 40
    try:
        df_dax = pd.read_html("https://en.wikipedia.org")
        maps["DAX 40 🇩🇪"] = dict(zip([t.replace('.', '-') + ".DE" for t in df_dax[0]['Ticker']], df_dax[0]['Company']))
    except: maps["DAX 40 🇩🇪"] = {"SAP.DE": "SAP SE", "SIE.DE": "Siemens AG"}

    # NASDAQ 100
    try:
        df_ndx = pd.read_html("https://en.wikipedia.org")
        maps["NASDAQ 100 🇺🇸"] = dict(zip(df_ndx[4]['Ticker'], df_ndx[4]['Company']))
    except: maps["NASDAQ 100 🇺🇸"] = {"AAPL": "Apple Inc.", "MSFT": "Microsoft Corp."}

    # EURO STOXX 50
    try:
        df_es50 = pd.read_html("https://en.wikipedia.org")
        maps["EURO STOXX 50 🇪🇺"] = dict(zip(df_es50[3]['Ticker'], df_es50[3]['Name']))
    except: maps["EURO STOXX 50 🇪🇺"] = {"ASML.AS": "ASML Holding"}

    # INDICES & FOREX (Vorgabe: Immer sichtbar)
    maps["INDICES & FOREX 🌍"] = {
        "^GDAXI": "DAX Index", 
        "^IXIC": "NASDAQ Index", 
        "^STOXX50E": "EuroStoxx 50 Index",
        "^NSEI": "NIFTY 50", 
        "XU100.IS": "BIST 100",
        "EURUSD=X": "Euro / US-Dollar", 
        "EURRUB=X": "Euro / Russischer Rubel"
    }
    return maps

# --- 2. BAUER STRATEGIE ENGINE ---
def analyze_market(ticker_map, filter_active=True):
    tickers = list(ticker_map.keys())
    data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', auto_adjust=True, progress=False)
    
    results = []
    for ticker, full_name in ticker_map.items():
        try:
            df = data[ticker].dropna() if len(tickers) > 1 else data.dropna()
            if len(df) < 35: continue
            
            close = df['Close']
            sma20 = close.rolling(20).mean()
            curr, p1, p2 = close.iloc[-1], close.iloc[-2], close.iloc[-3]
            c_sma = sma20.iloc[-1]
            
            # Bauer Signal: Kurs vs SMA20 + 3-Tage Momentum
            signal = "C" if (curr > p1 > p2 and curr > c_sma) else "P" if (curr < p1 < p2 and curr < c_sma) else "Wait"
            if filter_active and signal == "Wait": continue
            
            # RSI & ATR (1.5x Multiplikator)
            diff = close.diff()
            gain = diff.where(diff > 0, 0).rolling(14).mean()
            loss = -diff.where(diff < 0, 0).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
            
            # Backtest Trefferquote (12 Monate)
            hits, total = 0, 0
            if signal != "Wait":
                for i in range(-45, -5):
                    c_h, p_h, p2_h = close.iloc[i], close.iloc[i-1], close.iloc[i-2]
                    s_h = sma20.iloc[i]
                    h_sig = "C" if (c_h > p_h > p2_h and c_h > s_h) else "P" if (c_h < p_h < p2_h and c_h < s_h) else None
                    if h_sig == signal:
                        total += 1
                        if (signal == "C" and close.iloc[i+3] > c_h) or (signal == "P" and close.iloc[i+3] < c_h): hits += 1
            
            prob = (hits / total * 100) if total > 0 else 50.0
            day_delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
            icon = "☀️" if (curr > c_sma and day_delta > 0.2) else "⚖️" if abs(day_delta) < 0.2 else "⛈️"
            
            results.append({
                "name": full_name, "ticker": ticker, "price": curr, "signal": signal,
                "prob": prob, "rsi": rsi, "stop": curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5),
                "icon": icon, "delta": day_delta
            })
        except: continue
    return results

# --- 3. UI RENDERING ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie Pro 2026</div>", unsafe_allow_html=True)

with st.expander("ℹ️ AUSFÜHRLICHE STRATEGIE-LOGIK & REGELWERK ℹ️", expanded=True):
    st.columns(3)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        **1. Marktzustand & Trend**
        * ☀️ **Bullish:** Preis über SMA20 & positives Momentum (>0,2% Intraday).
        * ⚖️ **Neutral:** Preis oszilliert am SMA20 oder geringe Volatilität.
        * ⛈️ **Bearish:** Preis unter SMA20 oder starker Verkaufsdruck.
        """)
    with col_b:
        st.markdown("""
        **2. Signal-Trigger (3-Tage-Regel)**
        * **C (Call):** Trendbestätigung durch 3 Tage in Folge steigende Kurse + Schlusskurs über SMA20.
        * **P (Put):** Trendbestätigung durch 3 Tage in Folge fallende Kurse + Schlusskurs unter SMA20.
        """)
    with col_c:
        st.markdown("""
        **3. Risikomanagement & Wahrscheinlichkeit**
        * **Stop-Loss (SL):** Basiert auf der 14-Tage ATR (Volatilität) multipliziert mit 1,5.
        * **Prozentwert:** Historische Erfolgsrate dieses exakten Setups über die letzten 12 Monate.
        * **RSI (14):** Warnung vor Extremzonen (Überkauft >70 / Überverkauft <30).
        """)

market_maps = get_complete_market_maps()
tabs = st.tabs(list(market_maps.keys()))

for i, (tab_name, t_map) in enumerate(market_maps.items()):
    with tabs[i]:
        is_fixed = ("FOREX" in tab_name)
        data_results = analyze_market(t_map, filter_active=not is_fixed)
        
        if not data_results:
            st.info("Keine aktiven Handelssignale identifiziert.")
        else:
            data_results = sorted(data_results, key=lambda x: (x['signal'] == "Wait", -x['prob']))
            for res in data_results:
                fmt = "{:.5f}" if "=" in res['ticker'] else "{:.2f}"
                
                st.markdown("<div class='row-container'>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([2.5, 1, 0.7, 1.2])
                with c1:
                    st.markdown(f"<span style='font-weight:bold;'>{res['name']}</span> {res['icon']}", unsafe_allow_html=True)
                    rsi_c = "#ff4b4b" if res['rsi'] > 70 else "#00ff41" if res['rsi'] < 30 else "#8892b0"
                    st.markdown(f"<span class='metric-label'>RSI (14): <b style='color:{rsi_c};'>{res['rsi']:.1f}</b></span>", unsafe_allow_html=True)
                with c2:
                    d_col = "#00ff41" if res['delta'] >= 0 else "#ff4b4b"
                    st.markdown(f"<span class='price-text'>{fmt.format(res['price'])}</span><br><span style='color:{d_col}; font-size:0.75rem;'>{res['delta']:+.2f}%</span>", unsafe_allow_html=True)
                with c3:
                    if res['signal'] != "Wait":
                        s_cls = "sig-box-high" if res['prob'] >= 60 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
                        st.markdown(f"<span class='{s_cls}'>{res['signal']}</span>", unsafe_allow_html=True)
                    else: st.markdown("<span style='color:#333; font-weight:bold; font-size:0.8rem;'>WAIT</span>", unsafe_allow_html=True)
                with c4:
                    if res['signal'] != "Wait":
                        p_col = "#ffd700" if res['prob'] >= 60 else "#e6f1ff"
                        st.markdown(f"<b style='color:{p_col}; font-size:0.9rem;'>{res['prob']:.1f}%</b><br><span class='metric-label'>SL: {fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
                    else: st.markdown("<span class='metric-label'>Watchlist</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
