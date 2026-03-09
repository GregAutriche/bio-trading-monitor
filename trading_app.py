import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- SETUP & REFRESH ---
# Intervall: 5 Minuten (300.000ms)
st_autorefresh(interval=300000, key="datarefresh")
st.set_page_config(layout="wide", page_title="Momentum Strategy", page_icon="📡")

# --- STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    .header-text { font-size: 22px; font-weight: bold; margin-top: 20px; color: #ffd700 !important; }
    .update-info { text-align: right; color: #666; font-size: 0.85rem; margin-top: -15px; margin-bottom: 10px; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 10px 0 !important; line-height: 1.3 !important; }
    .sig-badge { padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85rem; }
    .sig-c { background-color: rgba(63, 185, 80, 0.2); color: #3fb950; border: 1px solid #3fb950; }
    .sig-p { background-color: rgba(0, 123, 255, 0.2); color: #007bff; border: 1px solid #007bff; }
    .mc-box { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #ffd700; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- KLARNAMEN MAPPING ---
NAME_MAP = {
    "EURUSD=X": "EURO / US-DOLLAR", "^GDAXI": "DAX 40 INDEX", "^STOXX50E": "EUROSTOXX 50", 
    "^IXIC": "NASDAQ COMPOSITE", "XU100.IS": "BIST 100 INDEX", "^NSEI": "NIFTY 50 INDEX",
    "SAN.MC": "BANCO SANTANDER", "ITX.MC": "INDITEX (ZARA)", "BBVA.MC": "BANCO BILBAO VIZCAYA",
    "SAP.DE": "SAP SE", "ADS.DE": "ADIDAS AG", "AAPL": "APPLE INC.", "NVDA": "NVIDIA CORP."
}

def get_name(t):
    return NAME_MAP.get(t, t.upper())

# --- CORE FUNCTIONS ---
@st.cache_data(ttl=300)
def fetch_batch_data(tickers):
    try:
        return yf.download(tickers, period="1y", interval="1d", auto_adjust=True, group_by='ticker', threads=False, timeout=10)
    except: return None

def process_signal(ticker, df):
    if df is None or df.empty or len(df) < 30: return None
    cp = df['Close']
    curr, prev, prev2 = cp.iloc[-1], cp.iloc[-2], cp.iloc[-3]
    sma20 = cp.rolling(20).mean().iloc[-1]
    
    delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
    icon = "☀️" if (curr > sma20 and delta > 0.2) else "⚖️" if abs(delta) < 0.2 else "⛈️"
    sig = "C" if curr > prev > prev2 and curr > sma20 else "P" if curr < prev < prev2 and curr < sma20 else "Wait"
    
    tr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
    sl = curr - (tr * 1.5) if sig == "C" else curr + (tr * 1.5) if sig == "P" else 0
    
    # Monte Carlo (1-Jahr Überlebensrate > 80% Kapital)
    rets = cp.pct_change().dropna()
    mc_surv = np.mean([np.prod(1 + np.random.choice(rets, 252, replace=True)) > 0.8 for _ in range(200)]) * 100
    
    return {"name": get_name(ticker), "ticker": ticker, "price": curr, "sig": sig, "icon": icon, "sl": sl, "delta": delta, "mc": mc_surv}

def render_row(res):
    st.markdown(f"""
    <div class="row-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 2;"><b>{res['name']}</b><br><small>{res['ticker']} | {res['price']:.2f}</small></div>
            <div style="flex: 1; text-align: center;">{res['icon']}<br><span style="color:{'#3fb950' if res['delta']>0 else '#007bff'}; font-size:0.8rem;">{res['delta']:+.2f}%</span></div>
            <div style="flex: 1; text-align: center;"><span class="sig-badge {'sig-c' if res['sig']=='C' else 'sig-p' if res['sig']=='P' else ''}">{res['sig']}</span></div>
            <div style="flex: 1; text-align: right;"><small>STOP-LOSS</small><br><b>{res['sl']:.2f}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- UI MAIN ---
now = datetime.now()
st.markdown(f"<div class='update-info'>Stand: {now.strftime('%d.%m.%Y | %H:%M:%S')} | Intervall: 5 Min.</div>", unsafe_allow_html=True)
st.markdown("<div class='header-text'>📡 MOMENTUM MONITOR</div>", unsafe_allow_html=True)

with st.expander("📘 Strategie-Leitfaden & Markt-Logik", expanded=False):
    st.markdown("""
    - **Trend-Erkennung**: Bestätigung durch 3-Tage-Preis-Action & SMA20-Filter.
    - **Wetter-Indikator**: Zeigt die kurzfristige Marktqualität (☀️ = Bullisch, ⛈️ = Riskant).
    - **Monte-Carlo (1J)**: Berechnet die statistische Überlebenswahrscheinlichkeit für ein Jahr.
    - **Signal-Logik**: **C** (Call/Long) über SMA20, **P** (Put/Short) unter SMA20.
    """)

# --- MACRO SECTION ---
st.markdown("<div class='header-text'>🌍 GLOBAL MACRO + INDICES 🌍</div>", unsafe_allow_html=True)
m_list = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]
m_data = fetch_batch_data(m_list)

if m_data is not None:
    for t in m_list:
        try:
            df = m_data[t] if len(m_list) > 1 else m_data
            res = process_signal(t, df)
            if res: render_row(res)
        except: continue

# --- SCREENER SECTION ---
st.markdown("<br><div class='header-text'>🔭 MARKT SCREENER</div>", unsafe_allow_html=True)
choice = st.radio("Region wählen:", ["IBEX 35", "DAX 40", "US Tech", "BIST 100"], horizontal=True, label_visibility="collapsed")

t_map = {
    "IBEX 35": ["SAN.MC", "ITX.MC", "BBVA.MC", "IBE.MC", "TEF.MC"],
    "DAX 40": ["SAP.DE", "ADS.DE", "ALV.DE", "SIE.DE", "BMW.DE"],
    "US Tech": ["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "META"],
    "BIST 100": ["THYAO.IS", "AKBNK.IS", "TUPRS.IS", "KCHOL.IS"]
}

if st.button("🚀 SCAN STARTEN 🚀", use_container_width=True):
    batch = fetch_batch_data(t_map[choice])
    results = []
    for t in t_map[choice]:
        try:
            df = batch[t] if len(t_map[choice]) > 1 else batch
            res = process_signal(t, df)
            if res: results.append(res)
            render_row(res)
        except: continue

    # --- TOP SIGNALE SORTIERT NACH MC ---
    st.markdown("<br><div class='header-text'>📈 TOP ANALYSE (SORTIERT NACH SICHERHEIT) 📈</div>", unsafe_allow_html=True)
    top_sigs = sorted([r for r in results if r['sig'] != "Wait"], key=lambda x: x['mc'], reverse=True)[:3]
    
    for r in top_sigs:
        st.markdown(f"""
        <div class="mc-box">
            <span class="sig-badge {'sig-c' if r['sig']=='C' else 'sig-p'}">{r['sig']}</span>
            <b style="color:#ffd700; font-size:1.1rem;">{r['name']}</b>
            <span style="color:#888; margin-left:15px;">Stop-Loss: {r['sl']:.2f}</span>
            <div style="margin-top:10px; color:#eee; font-size:0.9rem;">
                Überlebens-Rate (1J): <b style="color:#3fb950;">{r['mc']:.1f}%</b> | Wetter: {r['icon']}
            </div>
        </div>
        """, unsafe_allow_html=True)

