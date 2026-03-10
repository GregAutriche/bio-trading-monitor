import os
import sys
import math
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import base64
import io
from streamlit_autorefresh import st_autorefresh

# --- AUTO-INSTALLER ---
def install_and_import(package):
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        os.system(f"{sys.executable} -m pip install {package}")

install_and_import('streamlit-autorefresh')
install_and_import('lxml')
install_and_import('html5lib')

# --- SETUP ---
st_autorefresh(interval=60000, key="datarefresh")
st.set_page_config(layout="wide", page_title="Risk-Quant Strategy", page_icon="🛡️")

# --- STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .header-text { font-size: 24px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px; }
    .sig-box-p { color: #ff4b4b !important; border: 1px solid #ff4b4b; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-c { color: #3fb950 !important; border: 1px solid #3fb950; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-high { color: #ffd700 !important; border: 1px solid #ffd700; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .indicator-label { color: #888; font-size: 0.7rem; margin-top: 2px; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 15px 0; width: 100%; }
    .var-text { color: #ff4b4b; font-weight: bold; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE MATH FUNCTIONS ---

def create_visuals(hist_data, mc_results, last_price, color):
    # Sparkline (Vergangenheit)
    fig, ax = plt.subplots(figsize=(2.5, 0.5), dpi=70)
    ax.plot(hist_data.values, color=color, linewidth=2)
    ax.axis('off')
    buf_spark = io.BytesIO()
    fig.savefig(buf_spark, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    
    # MC-Cloud (Zukunft)
    fig, ax = plt.subplots(figsize=(2.5, 0.5), dpi=70)
    for i in range(min(40, len(mc_results))):
        ax.plot(mc_results[i, :], color='#ffd700', alpha=0.1, linewidth=0.6)
    ax.axhline(last_price, color='#555', linestyle='--', linewidth=0.8)
    ax.axis('off')
    buf_cloud = io.BytesIO()
    fig.savefig(buf_cloud, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    
    return base64.b64encode(buf_spark.getvalue()).decode(), base64.b64encode(buf_cloud.getvalue()).decode()

def run_monte_carlo_var(data, days=10, simulations=300):
    returns = np.log(data / data.shift(1)).dropna()
    mu, sigma = returns.mean(), returns.std()
    last_price = data.iloc[-1]
    
    results = np.zeros((simulations, days))
    for i in range(simulations):
        prices = [last_price]
        for _ in range(days):
            prices.append(prices[-1] * np.exp((mu - 0.5 * sigma**2) + sigma * np.random.normal()))
        results[i, :] = prices[1:]
    
    # Wahrscheinlichkeit für Kursanstieg
    prob_up = (results[:, -1] > last_price).sum() / simulations * 100
    
    # Value at Risk (VaR 95%): Das schlechteste 5% Perzentil
    final_returns = (results[:, -1] - last_price) / last_price
    var_95_pct = np.percentile(final_returns, 5) * 100
    
    return prob_up, var_95_pct, results

@st.cache_data(ttl=300)
def fetch_data(ticker):
    try:
        t_obj = yf.Ticker(ticker)
        df = t_obj.history(period="1y", interval="1d", auto_adjust=True)
        if len(df) < 35: return None
        
        curr = float(df['Close'].iloc[-1])
        prev = df['Close'].iloc[-2]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        
        # ATR für technischen Stop
        tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        
        # RSI
        delta_p = df['Close'].diff()
        gain = (delta_p.where(delta_p > 0, 0)).rolling(window=14).mean()
        loss = (-delta_p.where(delta_p < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain/(loss+1e-9))))
        
        # Monte Carlo & VaR
        prob_mc, var_95, mc_results = run_monte_carlo_var(df['Close'].tail(100))
        
        # Signal & Stop
        signal = "C" if (curr > prev and curr > sma20) else "P" if (curr < prev and curr < sma20) else "Wait"
        stop_price = curr - (atr*2) if signal=="C" else curr + (atr*2) if signal=="P" else 0
        
        # Risk-Check: Ist der Stop-Loss enger als das 95% Rauschen?
        stop_pct = abs((stop_price - curr) / curr) * 100
        risk_warning = "🚩" if stop_pct < abs(var_95) else ""

        spark_img, cloud_img = create_visuals(df['Close'].tail(20), mc_results, curr, "#3fb950" if curr >= prev else "#ff4b4b")
        
        return {
            "name": t_obj.info.get('shortName') or ticker, "ticker": ticker, "price": curr, 
            "delta": ((curr - df['Open'].iloc[-1])/df['Open'].iloc[-1])*100, "signal": signal, 
            "stop": stop_price, "prob": prob_mc, "var": var_95, "warning": risk_warning,
            "rsi": rsi.iloc[-1], "spark": spark_img, "cloud": cloud_img
        }
    except: return None

def render_row(res):
    fmt = "{:.4f}" if res['price'] < 5 else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([1.2, 0.6, 1.2, 0.6, 1.2])
    
    with c1: st.markdown(f"**{res['name']}**<br><small>{res['ticker']}</small><br><b>{fmt.format(res['price'])}</b>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div style='text-align:center; color:{'#3fb950' if res['delta']>=0 else '#ff4b4b'}; font-weight:bold;'>{res['delta']:+.2f}%</div>", unsafe_allow_html=True)
    
    with c3:
        st.markdown(f'<img src="data:image/png;base64,{res["spark"]}" width="110" title="Vergangenheit">', unsafe_allow_html=True)
        st.markdown(f'<img src="data:image/png;base64,{res["cloud"]}" width="110" style="opacity:0.6;" title="MC-Simulation">', unsafe_allow_html=True)
        st.markdown(f"<div class='indicator-label'>RSI: {res['rsi']:.1f}</div>", unsafe_allow_html=True)
        
    with c4:
        if res['signal'] != "Wait":
            cls = "sig-box-high" if res['prob'] >= 60 else ("sig-box-c" if res['signal']=="C" else "sig-box-p")
            st.markdown(f"<div style='margin-top:8px;'><span class='{cls}'>{res['signal']}</span></div>", unsafe_allow_html=True)

    with c5:
        if res['stop'] != 0:
            st.markdown(f"<span class='var-text'>VaR(95%): {res['var']:.2f}%</span> {res['warning']}", unsafe_allow_html=True)
            st.markdown(f"<small>SL-Level:</small> <b>{fmt.format(res['stop'])}</b><br><small>Prob: {res['prob']:.1f}%</small>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- UI MAIN ---
st.markdown("<div class='header-text'>📡 Risk-Quant Momentum Monitor 2026</div>", unsafe_allow_html=True)

# Quick Macro
m_list = ["EURUSD=X", "^GDAXI", "^IXIC", "BTC-USD"]
with ThreadPoolExecutor(max_workers=5) as ex:
    for r in [res for res in ex.map(fetch_data, m_list) if res]: render_row(r)

st.markdown("<br><div class='header-text'>🔭 Screener Engine</div>", unsafe_allow_html=True)
choice = st.selectbox("Markt wählen:", ["DAX 40", "Nasdaq 100", "BIST 100"])

if st.button("🚀 Markt-Scan starten"):
    # Vereinfachte Ticker-Listen für Demo (kannst du mit deiner get_live_tickers erweitern)
    tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "SAP.DE", "ALV.DE", "BMW.DE", "RHM.DE", "AMZN", "META"]
    with ThreadPoolExecutor(max_workers=10) as ex:
        results = [r for r in ex.map(fetch_data, tickers) if r]
        for r in sorted(results, key=lambda x: -x['prob']): render_row(r)

st.caption("ℹ️ VaR(95%): Statistisches Risiko für 10 Tage. 🚩 Warnung: Stop-Loss liegt im normalen Rauschbereich.")
