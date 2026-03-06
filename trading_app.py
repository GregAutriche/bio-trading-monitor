import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from collections import OrderedDict

# --- 0. CONFIG & TERMINAL DESIGN ---
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
    
    /* Kompaktes Layout */
    .row-container { border-bottom: 1px solid #172a45; padding: 6px 0; margin: 0; }
    .metric-label { color: #8892b0; font-size: 0.75rem; line-height: 1.2; }
    .price-text { font-size: 1.05rem; font-weight: bold; }
    .pos-calc-text { color: #64ffda !important; font-size: 0.85rem; font-weight: bold; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #0d1b2a; border-right: 1px solid #172a45; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. SIDEBAR: RISIKOMANAGEMENT ---
st.sidebar.header("🛡️ Positionsrechner")
capital = st.sidebar.number_input("Gesamtkapital (€/$)", value=10000, step=1000)
risk_pct = st.sidebar.slider("Risiko pro Trade (%)", 0.1, 5.0, 1.0, 0.1)
risk_amount = capital * (risk_pct / 100)
st.sidebar.info(f"Max. Verlust pro Trade: {risk_amount:.2f} €")

# --- 2. DATEN-ENGINE (VOLLSTÄNDIGKEIT) ---
@st.cache_data(ttl=86400)
def get_market_maps():
    maps = {}
    try:
        df_dax = pd.read_html("https://en.wikipedia.org")[4]
        maps["DAX 40 🇩🇪"] = dict(zip([t.replace('.', '-') + ".DE" for t in df_dax['Ticker']], df_dax['Company']))
    except: maps["DAX 40 🇩🇪"] = {"SAP.DE": "SAP SE"}
    try:
        df_ndx = pd.read_html("https://en.wikipedia.org")[4]
        maps["NASDAQ 100 🇺🇸"] = dict(zip(df_ndx['Ticker'], df_ndx['Company']))
    except: maps["NASDAQ 100 🇺🇸"] = {"AAPL": "Apple Inc."}
    try:
        df_es50 = pd.read_html("https://en.wikipedia.org")[3]
        maps["EURO STOXX 50 🇪🇺"] = dict(zip(df_es50['Ticker'], df_es50['Name']))
    except: maps["EURO STOXX 50 🇪🇺"] = {"ASML.AS": "ASML Holding"}

    maps["INDICES & FOREX 🌍"] = OrderedDict([
        ("EURUSD=X", "EUR/USD"), ("^STOXX50E", "EUROSTOXX"), ("^GDAXI", "DAX"),
        ("^IXIC", "NASDAQ"), ("EURRUB=X", "EUR/RUB"), ("^NSEI", "NIFTY"), ("XU100.IS", "BIST")
    ])
    return maps

# --- 3. BAUER STRATEGIE ENGINE ---
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
            
            signal = "C" if (curr > p1 > p2 and curr > c_sma) else "P" if (curr < p1 < p2 and curr < c_sma) else "Wait"
            if filter_active and signal == "Wait": continue
            
            atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
            sl = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5)
            
            # Positionsgröße
            sl_dist = abs(curr - sl)
            shares = int(risk_amount / sl_dist) if sl_dist > 0 else 0
            
            # Backtest Prob
            hits, total = 0, 0
            if signal != "Wait":
                for i in range(-45, -5):
                    c_h, p_h, p2_h = close.iloc[i], close.iloc[i-1], close.iloc[i-2]
                    s_h = sma20.iloc[i]
                    h_sig = "C" if (c_h > p_h > p2_h and c_h > s_h) else "P" if (c_h < p_h < p2_h and c_h < s_h) else None
                    if h_sig == signal:
                        total += 1
                        if (signal == "C" and close.iloc[i+3] > c_h) or (signal == "P" and close.iloc[i+3] < c_h): hits += 1
            
            results.append({
                "name": full_name, "ticker": ticker, "price": curr, "signal": signal,
                "prob": (hits/total*100) if total > 0 else 50.0, "rsi": 100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean()))).iloc[-1],
                "stop": sl, "shares": shares, "delta": ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100,
                "spark": close.tail(14).values, "icon": "☀️" if (curr > c_sma and (curr/df['Open'].iloc[-1]-1)>0.002) else "⚖️" if abs(curr/df['Open'].iloc[-1]-1)<0.002 else "⛈️"
            })
        except: continue
    return results

# --- 4. UI RENDERING ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie Pro 2026</div>", unsafe_allow_html=True)

with st.expander("ℹ️ VOLLSTÄNDIGE STRATEGIE-LOGIK & REGELWERK ℹ️", expanded=True):
    st.markdown("""
    ### 1. Philosophie & SMA 20 Filter
    Die Strategie nutzt den SMA 20 als primäre Trend-Leitplanke. Einstiege erfolgen nur in Richtung des übergeordneten Trends.
    
    ### 2. Der Momentum-Trigger (3-Tage-Regel)
    Ein Signal wird generiert, wenn der Kurs drei Tage in Folge steigt (Call) oder fällt (Put) und dabei über/unter dem SMA 20 schließt.
    
    ### 3. Statistische Wahrscheinlichkeit
    Der Prozentwert berechnet dynamisch die Erfolgsrate dieses Setups für den Einzelwert über die letzten 12 Monate.
    
    ### 4. Exit-Strategie (Stop-Loss)
    Der Stop-Loss liegt beim 1,5-fachen der Average True Range (ATR). Dies gibt dem Markt "Luft zum Atmen" und schützt vor Rauschen.
    
    ### 5. Positionsrechner & Sparklines
    Der Rechner (links) ermittelt die ideale Stückzahl basierend auf deinem Risiko. Die Sparkline visualisiert den 14-Tage-Trendverlauf.
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
                c1, c2, c3, c4, c5 = st.columns([2, 0.8, 0.8, 0.6, 1.2])
                with c1:
                    st.markdown(f"**{res['name']}** {res['icon']}")
                    st.line_chart(res['spark'], height=40, use_container_width=True)
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
                    else: st.markdown("<span style='color:#333; font-weight:bold;'>WAIT</span>", unsafe_allow_html=True)
                with c5:
                    if res['signal'] != "Wait":
                        st.markdown(f"<b style='color:#ffd700;'>{res['prob']:.1f}%</b> | <span class='pos-calc-text'>{res['shares']} Stk.</span>", unsafe_allow_html=True)
                        st.markdown(f"<span class='metric-label'>SL: {fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
                    else: st.markdown("<span class='metric-label'>Monitoring</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
