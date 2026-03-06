import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import base64
import io
import matplotlib.pyplot as plt

# --- 0. AUTO-REFRESH & SETUP ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    import os
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

# Automatischer Refresh auf 60 Sekunden erhöht (Schont die API-Rate)
st_autorefresh(interval=60000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .header-text { font-size: 24px; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-c { color: #3fb950 !important; border: 1px solid #3fb950 !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-high { color: #ffd700 !important; border: 1px solid #ffd700 !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sl-label { color: #888; font-size: 0.85rem; }
    .sl-value { color: #e0e0e0; font-weight: bold; font-size: 1.1rem; }
    .indicator-label { color: #888; font-size: 0.75rem; margin-top: 2px; }
    .kurs-label { color: #888; font-size: 0.85rem; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 12px 0; width: 100%; align-items: center; }
    .scan-info { color: #ffd700; font-style: italic; font-size: 0.9rem; margin-bottom: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HILFSFUNKTIONEN (CHARTS) ---
def create_sparkline(data, color):
    """Erzeugt ein kleines Base64-Bild für den Kursverlauf (Sparkline)."""
    plt.figure(figsize=(2, 0.5), dpi=80)
    plt.plot(data.values, color=color, linewidth=2)
    plt.axis('off')
    plt.gca().set_facecolor((0,0,0,0))
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode()

# --- 3. DATEN-ENGINE ---
@st.cache_data(ttl=300)
def get_historical_data(ticker):
    try:
        t_obj = yf.Ticker(ticker)
        df = t_obj.history(period="1y", interval="1d", auto_adjust=True)
        if df.empty or len(df) < 35: return None, None
        return df, t_obj.info.get('shortName') or ticker
    except: return None, None

def calculate_indicators(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = tr.rolling(window=14).mean()
    # Vereinfachter ADX für Performance
    df['ADX'] = (abs(df['High'].diff() - abs(df['Low'].diff())) / tr).rolling(window=14).mean() * 100
    return df, atr.iloc[-1]

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

def fetch_data(ticker):
    df, name = get_historical_data(ticker)
    if df is None: return None
    
    df, last_atr = calculate_indicators(df)
    curr = float(df['Close'].iloc[-1])
    prev, prev2 = df['Close'].iloc[-2], df['Close'].iloc[-3]
    open_t = df['Open'].iloc[-1]
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    
    rsi_val = df['RSI'].iloc[-1]
    adx_val = df['ADX'].iloc[-1]
    
    signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
    delta = ((curr - open_t) / open_t) * 100
    stop = curr - (last_atr * 1.5) if signal == "C" else curr + (last_atr * 1.5) if signal == "P" else 0
    icon = "☀️" if (curr > sma20 and delta > 0.3) else "⚖️" if abs(delta) < 0.3 else "⛈️"
    
    # Letzte 20 Tage für Sparkline
    spark_data = df['Close'].tail(20)
    spark_color = "#3fb950" if curr > spark_data.iloc[0] else "#007bff"
    spark_img = create_sparkline(spark_data, spark_color)
    
    return {
        "display_name": name, "ticker": ticker, "price": curr, 
        "delta": delta, "signal": signal, "stop": stop, "icon": icon, 
        "prob": calculate_probability(df, signal), "rsi": rsi_val, "adx": adx_val,
        "sparkline": spark_img
    }

# --- 4. UI RENDERER ---
def render_row(res):
    if not res: return
    fmt = "{:.6f}" if ("=" in res['ticker']) else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([1.2, 0.6, 0.8, 0.5, 1.0])
    
    with c1:
        rsi_c = "#ff4b4b" if res['rsi'] > 70 else "#3fb950" if res['rsi'] < 30 else "#888"
        adx_c = "#ffd700" if res['adx'] > 25 else "#888"
        st.markdown(f"**{res['display_name']}**<br><span class='kurs-label'>{fmt.format(res['price'])}</span>", unsafe_allow_html=True)
    
    with c2:
        color = "#3fb950" if res['delta'] >= 0 else "#007bff"
        st.markdown(f"<div style='text-align:center;'>{res['icon']}<br><span style='color:{color}; font-size:0.85rem;'>{res['delta']:+.2f}%</span></div>", unsafe_allow_html=True)
    
    with c3: # NEU: Sparkline
        st.markdown(f'<img src="data:image/png;base64,{res["sparkline"]}" width="100">', unsafe_allow_html=True)
        st.markdown(f"<span class='indicator-label'>RSI: <b style='color:{rsi_c};'>{res['rsi']:.1f}</b> | ADX: <b style='color:{adx_c};'>{res['adx']:.1f}</b></span>", unsafe_allow_html=True)

    with c4:
        if res['signal'] != "Wait":
            cls = "sig-box-high" if res['prob'] >= 60.0 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
            st.markdown(f"<span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
        else: st.markdown("<span style='color:#444;'>-</span>", unsafe_allow_html=True)
            
    with c5:
        if res['stop'] != 0:
            prob_txt = f"<span style='color:#ffd700; font-weight:bold;'>{res['prob']:.1f}%</span>" if res['prob'] >= 60.0 else f"<span style='color:#888;'>({res['prob']:.1f}%)</span>"
            st.markdown(f"<span class='sl-label'>SL</span> {prob_txt}<br><span class='sl-value'>{fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. MAIN APP ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie 📡</div>", unsafe_allow_html=True)
st.write(f"Update: {datetime.now().strftime('%H:%M:%S')} | Refresh: 60s")

with st.expander("ℹ️ Strategie-Leitfaden 2026", expanded=False):
    st.markdown("""
    - **☀️ Bullish / ⛈️ Bearish:** Trend-Zustand vs. SMA20.
    - **Chart:** Letzte 20 Handelstage (Trend-Visualisierung).
    - **Wahrscheinlichkeit:** Historische Trefferrate (Gold ab 60%).
    - **ADX:** Trendstärke (>25 ist stark).
    """, unsafe_allow_html=True)

# --- 6. MACRO SECTION ---
st.markdown("<div class='header-text'>🌍 Macro + Indices 🌍</div>", unsafe_allow_html=True)
macro_tickers = ["EURUSD=X", "^GDAXI", "^IXIC", "BTC-USD"]
for t in macro_tickers:
    render_row(fetch_data(t))

# --- 7. SCANNER SECTION ---
st.markdown("<br><div class='header-text'>🔭 Markt Screener 🔭</div>", unsafe_allow_html=True)
index_data = {
    "DAX 40": ["ADS.DE", "ALV.DE", "BAS.DE", "SAP.DE", "SIE.DE"],
    "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL"],
    "BIST 100": ["THYAO.IS", "TUPRS.IS", "AKBNK.IS"]
}

with st.expander("Screener-Einstellungen", expanded=True):
    col_sel, col_btn = st.columns(2)
    if 'scan_active' not in st.session_state: st.session_state.scan_active = False
    with col_sel: choice = st.radio("Markt:", list(index_data.keys()), horizontal=True)
    with col_btn:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🚀 Scan Start/Stop", use_container_width=True):
            st.session_state.scan_active = not st.session_state.scan_active

if st.session_state.scan_active:
    st.markdown(f"<div class='scan-info'>Scanne {choice}...</div>", unsafe_allow_html=True)
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(fetch_data, index_data[choice]))
        signal_hits = [r for r in results if r is not None and r['signal'] != "Wait"]
        if signal_hits:
            for r in sorted(signal_hits, key=lambda x: (x['prob'] < 60.0, -x['prob'])): render_row(r)
        else: st.info("Keine aktiven Signale.")

# --- 8. BACKTESTING (FIX FÜR NAME-ERROR) ---
st.markdown("---")
with st.expander("📈 Detailliertes Backtesting (Bsp. Microsoft)"):
    msft_res = fetch_data("MSFT")
    if msft_res:
        st.write(f"Analyse für **{msft_res['display_name']}**")
        st.metric("Historische Quote", f"{msft_res['prob']:.1f}%", delta=f"{msft_res['adx']:.1f} ADX")
