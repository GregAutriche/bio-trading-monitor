import os
import sys

# --- AUTO-INSTALLER ---
def install_and_import(package):
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        os.system(f"{sys.executable} -m pip install {package}")

install_and_import('streamlit-autorefresh')
install_and_import('lxml')
install_and_import('html5lib')
install_and_import('yfinance')

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- SETUP & REFRESH ---
# Intervall auf 5 Minuten, um API-Sperren zu vermeiden
st_autorefresh(interval=300000, key="datarefresh")
st.set_page_config(layout="wide", page_title="Momentum Strategy", page_icon="📡")

# --- STYLING (LESBARKEIT & KOMPAKTHEIT) ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    [data-testid="column"] { padding: 0px 6px !important; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    .header-text { font-size: 19px; font-weight: bold; margin-top: 12px; margin-bottom: 4px; color: #ffd700 !important; }
    
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff !important; padding: 1px 5px; border-radius: 4px; font-weight: bold; font-size: 0.75rem; }
    .sig-box-c { color: #3fb950 !important; border: 1px solid #3fb950 !important; padding: 1px 5px; border-radius: 4px; font-weight: bold; font-size: 0.75rem; }
    .sig-box-high { color: #ffd700 !important; border: 1px solid #ffd700 !important; padding: 1px 5px; border-radius: 4px; font-weight: bold; font-size: 0.75rem; }
    
    .indicator-label { color: #777; font-size: 0.68rem; margin-top: -1px; display: block; }
    
    /* Zeilenhöhe für Tabellen */
    .row-container { border-bottom: 1px solid #1a202c; padding: 3px 0 !important; width: 100%; line-height: 1.1 !important; }
    
    /* Monte-Carlo Boxen (Optimierte Lesbarkeit) */
    .mc-box { 
        background-color: #161b22; 
        padding: 12px; 
        border-radius: 8px; 
        border: 1px solid #30363d; 
        margin-top: 10px; 
        margin-bottom: 10px;
        font-size: 0.88rem; 
        color: #ffffff !important; 
        line-height: 1.5 !important;
    }
    .mc-label { color: #8b949e; font-size: 0.78rem; }
    
    small { font-size: 0.7rem; color: #888; }
    b { font-size: 0.82rem; color: #eeeeee; }
    </style>
    """, unsafe_allow_html=True)

# --- KLARNAMEN MAPPING ---
NAME_MAP = {
    "EURUSD=X": "EURO / US-DOLLAR", "^GDAXI": "DAX 40 INDEX", "^STOXX50E": "EUROSTOXX 50 INDEX", 
    "^IXIC": "NASDAQ COMPOSITE", "XU100.IS": "BIST 100 INDEX", "^NSEI": "NIFTY 50 INDEX",
    "THYAO.IS": "TURKISH AIRLINES", "AKBNK.IS": "AKBANK", "EREGL.IS": "ERDEMIR CELIK",
    "TUPRS.IS": "TUPRAS PETROL", "SISE.IS": "SISECAM", "KCHOL.IS": "KOC HOLDING",
    "AAPL": "APPLE INC.", "MSFT": "MICROSOFT CORP.", "NVDA": "NVIDIA CORP.", "TSLA": "TESLA INC.",
    "ADS.DE": "ADIDAS AG", "SAP.DE": "SAP SE", "SIE.DE": "SIEMENS AG", "AIR.DE": "AIRBUS SE",
    "ALV.DE": "ALLIANZ SE", "BAS.DE": "BASF SE", "BMW.DE": "BMW AG"
}

@st.cache_data(ttl=3600)
def get_name_safe(ticker):
    if ticker in NAME_MAP: return NAME_MAP[ticker]
    try:
        t_obj = yf.Ticker(ticker)
        name = t_obj.info.get('shortName') or t_obj.info.get('longName') or ticker
        return name.upper()
    except:
        return ticker.replace(".IS", "").replace(".DE", "").upper()

# --- CORE FUNCTIONS ---

def sparkline_svg(series, color="#3fb950"):
    values = list(series.values)
    if len(values) < 2: return ""
    min_v, max_v = min(values), max(values)
    span = max_v - min_v if max_v != min_v else 1.0
    norm = [(v - min_v) / span for v in values]
    points = " ".join(f"{i},{1 - v}" for i, v in enumerate(norm))
    width = max(len(values) - 1, 1)
    return f'<svg width="95" height="20" viewBox="0 0 {width} 1" xmlns="http://www.w3.org"><polyline fill="none" stroke="{color}" stroke-width="0.12" points="{points}" /></svg>'

@st.cache_data(ttl=300, show_spinner=False)
def fetch_batch_data(tickers):
    if not tickers: return {}
    try:
        data = yf.download(tickers=tickers, period="1y", interval="1d", auto_adjust=True, group_by='ticker', threads=False, timeout=10)
        if data is None or data.empty: return {}
        result = {}
        if len(tickers) > 1 and isinstance(data.columns, pd.MultiIndex):
            for t in tickers:
                if t in data.columns.get_level_values(0):
                    df_t = data.xs(t, axis=1, level=0).dropna()
                    if not df_t.empty: result[t] = df_t
        else:
            if not data.empty:
                t_key = tickers[0] if isinstance(tickers, list) else tickers
                result[t_key] = data.dropna()
        return result
    except: return {}

def compute_signal_from_df(ticker, df):
    try:
        if df is None or df.empty or len(df) < 35: return None
        cp = df['Close']
        curr, prev, prev2 = cp.iloc[-1], cp.iloc[-2], cp.iloc[-3]
        sma20 = cp.rolling(20).mean().iloc[-1]
        
        delta_p = cp.diff()
        gain = delta_p.where(delta_p > 0, 0).rolling(14).mean()
        loss = (-delta_p.where(delta_p < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        tr = pd.concat([df['High']-df['Low'], (df['High']-cp.shift()).abs(), (df['Low']-cp.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        adx = ((df['High'].diff().abs() - df['Low'].diff().abs()).abs() / (tr + 1e-9)).rolling(14).mean().iloc[-1] * 100
        daily_delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
        
        signal = "C" if curr > prev > prev2 and curr > sma20 else ("P" if curr < prev < prev2 and curr < sma20 else "Wait")
        
        return {
            "name": get_name_safe(ticker), "ticker": ticker, "price": float(curr), "delta": daily_delta,
            "signal": signal, "stop": curr-(atr*1.5) if signal=="C" else (curr+(atr*1.5) if signal=="P" else 0),
            "prob": 64.0 if adx > 25 else 52.0, "rsi": rsi.iloc[-1], "adx": adx, 
            "icon": "☀️" if (curr>sma20 and daily_delta>0.2) else ("⚖️" if abs(daily_delta)<0.2 else "⛈️"),
            "spark": sparkline_svg(cp.tail(20), "#3fb950" if curr>=prev else "#007bff")
        }
    except: return None

def monte_carlo_sim(df, sims=250):
    if df is None or len(df) < 50: return None
    rets = df['Close'].pct_change().dropna()
    res = [np.prod(1 + np.random.choice(rets, 252, replace=True)) for _ in range(sims)]
    return {"median": np.median(res), "worst": np.min(res), "survival": np.mean(np.array(res) > 0.8) * 100}

def render_row(res):
    fmt = "{:.6f}" if "=" in res['ticker'] else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([2.0, 0.5, 0.8, 0.5, 0.8])
    with c1: st.markdown(f"**{res['name']}**<br><small>{res['ticker']} | {fmt.format(res['price'])}</small>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div style='text-align:center;'>{res['icon']}<br><span style='color:{'#3fb950' if res['delta']>=0 else '#007bff'}; font-size:0.75rem;'>{res['delta']:+.2f}%</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(res["spark"], unsafe_allow_html=True)
        st.markdown(f"<span class='indicator-label'>RSI {res['rsi']:.0f} ADX {res['adx']:.0f}</span>", unsafe_allow_html=True)
    with c4:
        if res['signal'] != "Wait":
            cls = "sig-box-high" if res['prob'] >= 60 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
            st.markdown(f"<div style='margin-top:4px;'><span class='{cls}'>{res['signal']}</span></div>", unsafe_allow_html=True)
    with c5:
        if res['stop'] != 0: st.markdown(f"<small>SL {res['prob']:.0f}%</small><br><b>{fmt.format(res['stop'])}</b>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- UI MAIN ---
st.markdown("<div class='header-text'>📡 MOMENTUM STRATEGIE MONITOR</div>", unsafe_allow_html=True)

with st.expander("📘 Ausführlicher Strategie‑Leitfaden & Markt‑Logik", expanded=False):
    st.markdown("""
    ### 🧭 Überblick des Systems
    Identifiziert Momentum-Ausbrüche basierend auf Preis-Action und Trendfiltern.
    - **Trend-Logik**: Signal bei 3-Tage-Folge über/unter SMA20.
    - **Indikatoren**: RSI (Überkauft/Überverkauft) & ADX (Trendstärke).
    - **Monte-Carlo**: Simuliert 250 synthetische Jahresverläufe für Risiko-Assessments.
    - **Stop-Loss**: Basiert auf der 1.5-fachen ATR (Volatilität).
    """)

# --- MACRO ---
st.markdown("<div class='header-text'>🌍 GLOBAL MACRO</div>", unsafe_allow_html=True)
m_list = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]
m_data = fetch_batch_data(m_list)
if m_data:
    for t in m_list:
        df = m_data.get(t)
        if df is not None:
            res = compute_signal_from_df(t, df)
            if res: render_row(res)

# --- SCREENER ---
st.markdown("<br><div class='header-text'>🔭 MARKT SCREENER</div>", unsafe_allow_html=True)
choice = st.radio("Index:", ["DAX 40", "Nasdaq 100", "EuroStoxx 50", "BIST 100"], horizontal=True, label_visibility="collapsed")
if st.button("🚀 SCAN START/STOP", use_container_width=True): 
    st.session_state.scan_active = not st.session_state.get('scan_active', False)

if st.session_state.get('scan_active', False):
    t_lists = {
        "DAX 40": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "SAP.DE", "SIE.DE", "DTE.DE", "VOW3.DE"],
        "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL", "META", "AVGO", "COST", "NFLX", "ADBE", "AMD"],
        "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA", "SIE.DE", "AIR.PA", "SAN.MC", "ITX.MC", "CS.PA", "BNP.PA"],
        "BIST 100": ["THYAO.IS", "AKBNK.IS", "EREGL.IS", "TUPRS.IS", "SISE.IS", "KCHOL.IS", "ASELS.IS", "BIMAS.IS", "GARAN.IS", "ISCTR.IS", "SAHOL.IS", "YKBNK.IS", "PGSUS.IS"]
    }
    tickers = t_lists.get(choice, ["AAPL"])
    batch = fetch_batch_data(tickers)
    results = []
    for t in tickers:
        df = batch.get(t)
        if df is not None:
            res = compute_signal_from_df(t, df)
            if res: 
                results.append(res)
                render_row(res)

    # --- TOP 3 RISK ANALYSIS ---
    st.markdown("<br><div class='header-text'>📈 RISK ANALYSIS (MONTE-CARLO)</div>", unsafe_allow_html=True)
    top_3 = sorted([r for r in results if r['signal'] != "Wait"], key=lambda x: -x['prob'])[:3]
    if top_3:
        for res in top_3:
            mc = monte_carlo_sim(batch.get(res['ticker']))
            if mc:
                st.markdown(f"""
                <div class='mc-box'>
                    <span style='font-size: 0.95rem; font-weight: bold; color: #ffd700;'>{res['name']}</span><br>
                    <span class='mc-label'>Überlebens-Quote:</span> <span style='color:#3fb950; font-weight:bold;'>{mc['survival']:.0f}%</span> | 
                    <span class='mc-label'>Median:</span> <span style='color:#ffffff; font-weight:bold;'>{mc['median']:.2f}</span> | 
                    <span class='mc-label'>Schlechtester Verlauf:</span> <span style='color:#ff4b4b; font-weight:bold;'>{mc['worst']:.2f}</span>
                </div>
                """, unsafe_allow_html=True)
