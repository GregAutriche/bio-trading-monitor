import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from collections import OrderedDict

# --- 0. CONFIG & PROFESSIONAL NAVY DESIGN ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

st.markdown("""
    <style>
    .stApp { background-color: #0a192f; }
    h1, h2, h3, p, span, label, div { color: #e6f1ff !important; font-family: 'Segoe UI', sans-serif; }
    .header-text { font-size: 26px; font-weight: bold; color: #64ffda !important; border-bottom: 2px solid #64ffda; padding-bottom: 5px; margin-bottom: 15px; }
    
    /* Signal Design */
    .sig-box-c { color: #00ff41 !important; border: 1px solid #00ff41; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(0, 255, 65, 0.1); }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(0, 123, 255, 0.1); }
    .sig-box-high { color: #ffd700 !important; border: 2px solid #ffd700; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(255, 215, 0, 0.2); }
    
    /* Kompaktes Zeilenlayout - FIX: Verhindert weiße Boxen */
    .row-container { border-bottom: 1px solid #172a45; padding: 6px 0; margin: 0; }
    .metric-label { color: #8892b0; font-size: 0.75rem; line-height: 1.2; }
    .price-text { font-size: 1.1rem; font-weight: bold; }
    
    /* Sparkline-Fix: Entfernt Achsen, Labels und weißen Hintergrund */
    [data-testid="stVegaLiteChart"] canvas { filter: brightness(0.8) !important; }
    .stVegaLiteChart { margin-top: -25px !important; background-color: transparent !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0d1b2a; border-right: 1px solid #172a45; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. SIDEBAR: RISIKOMANAGEMENT ---
st.sidebar.header("🛡️ Positionsrechner")
capital = st.sidebar.number_input("Gesamtkapital (€/$)", value=10000, step=1000)
risk_pct = st.sidebar.slider("Risiko pro Trade (%)", 0.1, 5.0, 1.0, 0.1)
risk_amount = capital * (risk_pct / 100)
st.sidebar.info(f"Max. Risiko: {risk_amount:.2f} €")

# --- 2. MARKT-MAPPING ---
@st.cache_data(ttl=86400)
def get_market_maps():
    maps = {}
    try:
        df_dax = pd.read_html("https://en.wikipedia.org")
        maps["DAX 40 🇩🇪"] = dict(zip([t.replace('.', '-') + ".DE" for t in df_dax['Ticker']], df_dax['Company']))
    except: maps["DAX 40 🇩🇪"] = {"SAP.DE": "SAP SE"}
    try:
        df_ndx = pd.read_html("https://en.wikipedia.org")
        maps["NASDAQ 100 🇺🇸"] = dict(zip(df_ndx['Ticker'], df_ndx['Company']))
    except: maps["NASDAQ 100 🇺🇸"] = {"AAPL": "Apple Inc."}
    try:
        df_es50 = pd.read_html("https://en.wikipedia.org")
        maps["EURO STOXX 50 🇪🇺"] = dict(zip(df_es50['Ticker'], df_es50['Name']))
    except: maps["EURO STOXX 50 🇪🇺"] = {"ASML.AS": "ASML Holding"}

    # REIHENFOLGE WIE BESPROCHEN
    maps["INDICES & FOREX 🌍"] = OrderedDict([
        ("EURUSD=X", "EUR/USD"), ("^STOXX50E", "EUROSTOXX"), ("^GDAXI", "DAX"),
        ("^IXIC", "NASDAQ"), ("EURRUB=X", "EUR/RUB"), ("^NSEI", "NIFTY"), ("XU100.IS", "BIST")
    ])
    return maps

# --- 3. ANALYSE ENGINE ---
def analyze_market(ticker_map, filter_active=True):
    tickers = list(ticker_map.keys())
    data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', auto_adjust=True, progress=False)
    results = []
    for ticker, full_name in ticker_map.items():
        try:
            df = data[ticker].dropna() if len(tickers) > 1 else data.dropna()
            if len(df) < 40: continue
            close = df['Close']
            sma20 = close.rolling(20).mean()
            curr, p1, p2 = close.iloc[-1], close.iloc[-2], close.iloc[-3]
            c_sma = sma20.iloc[-1]
            
            signal = "C" if (curr > p1 > p2 and curr > c_sma) else "P" if (curr < p1 < p2 and curr < c_sma) else "Wait"
            if filter_active and signal == "Wait": continue
            
            atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
            sl = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5)
            sl_dist = abs(curr - sl)
            shares = int(risk_amount / sl_dist) if sl_dist > 0 else 0
            
            # RSI & Wahrscheinlichkeit
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean()
            rsi = 100 - (100 / (1 + (g/l))).iloc[-1]
            
            hits, total = 0, 0
            if signal != "Wait":
                for i in range(-50, -5):
                    c_h, p_h, p2_h = close.iloc[i], close.iloc[i-1], close.iloc[i-2]
                    s_h = sma20.iloc[i]
                    if signal == "C" and c_h > p_h > p2_h and c_h > s_h:
                        total += 1
                        if close.iloc[i+3] > c_h: hits += 1
                    elif signal == "P" and c_h < p_h < p2_h and c_h < s_h:
                        total += 1
                        if close.iloc[i+3] < c_h: hits += 1
            
            results.append({
                "name": full_name, "ticker": ticker, "price": curr, "signal": signal,
                "prob": (hits/total*100) if total > 0 else 50.0, "rsi": rsi, "stop": sl, "shares": shares,
                "delta": ((curr/df['Open'].iloc[-1])-1)*100, "spark": close.tail(20), 
                "icon": "☀️" if (curr > c_sma and (curr/df['Open'].iloc[-1]-1)>0.002) else "⚖️" if abs(curr/df['Open'].iloc[-1]-1)<0.002 else "⛈️"
            })
        except: continue
    return results

# --- 4. UI ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie Pro 2026</div>", unsafe_allow_html=True)

with st.expander("ℹ️ VOLLSTÄNDIGER STRATEGIE-LEITFADEN ℹ️", expanded=True):
    st.markdown("""
    ### 1. SMA 20 Trend-Filter & Marktzustand
    Der SMA 20 dient als Hauptfilter. Symbole: ☀️ (Bullish/Über SMA), ⚖️ (Neutral), ⛈️ (Bearish/Unter SMA).
    ### 2. 3-Tage Momentum-Regel
    Einstieg erfolgt erst, wenn der Preis 3 aufeinanderfolgende Tage die Trendrichtung bestätigt (steigend für Call, fallend für Put).
    ### 3. Statistische Wahrscheinlichkeit
    Prozentwert der erfolgreichen Trades basierend auf dem exakten 3-Tage-Setup der letzten 12 Monate.
    ### 4. Risikomanagement (ATR-Stop)
    Stopp-Loss bei 1,5x ATR. Der Positionsrechner (links) zeigt die exakte Stückzahl basierend auf deinem Kontostand.
    """)

m_maps = get_market_maps()
tabs = st.tabs(list(m_maps.keys()))

for i, (tab_name, t_map) in enumerate(m_maps.items()):
    with tabs[i]:
        is_fixed = ("FOREX" in tab_name)
        data_results = analyze_market(t_map, filter_active=not is_fixed)
        if not data_results: st.info("Keine aktiven Signale.")
        else:
            if not is_fixed: data_results = sorted(data_results, key=lambda x: -x['prob'])
            for res in data_results:
                fmt = "{:.5f}" if "=" in res['ticker'] else "{:.2f}"
                st.markdown("<div class='row-container'>", unsafe_allow_html=True)
                c1, c2, c3, c4, c5 = st.columns([2.2, 0.8, 0.8, 0.6, 1.2])
                with c1:
                    st.markdown(f"**{res['name']}** {res['icon']}")
                    # Sparkline-Fix: Nutze area_chart mit CSS-Fix
                    st.area_chart(res['spark'], height=40, use_container_width=True)
                with c2:
                    st.markdown(f"<span class='price-text'>{fmt.format(res['price'])}</span>", unsafe_allow_html=True)
                    rsi_col = "#ff4b4b" if res['rsi'] > 70 else "#00ff41" if res['rsi'] < 30 else "#8892b0"
                    st.markdown(f"<span class='metric-label'>RSI: <b style='color:{rsi_col};'>{res['rsi']:.1f}</b></span>", unsafe_allow_html=True)
                with c3:
                    d_col = "#00ff41" if res['delta'] >= 0 else "#ff4b4b"
                    st.markdown(f"<span style='color:{d_col}; font-weight:bold;'>{res['delta']:+.2f}%</span>", unsafe_allow_html=True)
                with c4:
                    if res['signal'] != "Wait":
                        s_cls = "sig-box-high" if res['prob'] >= 60 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
                        st.markdown(f"<span class='{s_cls}'>{res['signal']}</span>", unsafe_allow_html=True)
                    else: st.markdown("<span style='color:#444; font-weight:bold;'>WAIT</span>", unsafe_allow_html=True)
                with c5:
                    if res['signal'] != "Wait":
                        p_col = "#ffd700" if res['prob'] >= 60 else "#e6f1ff"
                        st.markdown(f"<b style='color:{p_col};'>{res['prob']:.1f}%</b> | **{res['shares']} Stk.**", unsafe_allow_html=True)
                        st.markdown(f"<span class='metric-label'>SL: {fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
                    else: st.markdown("<span class='metric-label'>Monitoring</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
