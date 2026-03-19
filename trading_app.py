import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. NAMENS-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "^GDAXI": "DAX Index", "^STOXX50E": "EuroStoxx 50",
    "AAPL": "Apple (US)", "NVDA": "Nvidia (US)", "TSLA": "Tesla (US)", 
    "SAP.DE": "SAP (DE)", "ADS.DE": "Adidas (DE)", "DBK.DE": "Deutsche Bank (DE)"
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }
    .metric-value { font-size: 1.2rem; font-weight: bold; color: white; }
    h1, h2, h3 { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="1d"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def get_options_data(ticker_str):
    try:
        tk = yf.Ticker(ticker_str)
        if not tk.options: return None, None
        opt = tk.option_chain(tk.options[0])
        return opt.calls.sort_values("openInterest", ascending=False).head(5), \
               opt.puts.sort_values("openInterest", ascending=False).head(5)
    except: return None, None

# --- 5. DASHBOARD HEADER ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# Schnellübersicht oben
m_symbols = ["EURUSD=X", "^GDAXI", "^STOXX50E", "AAPL", "NVDA", "SAP.DE"]
cols_m = st.columns(len(m_symbols))
for i, t in enumerate(m_symbols):
    df_m = get_data(t, period="5d")
    if not df_m.empty:
        l = float(df_m['Close'].iloc[-1])
        c = ((l / df_m['Close'].iloc[-2]) - 1) * 100
        cols_m[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><div class="metric-value">{l:,.2f}</div>'
                           f'<span style="color:{"#00FFA3" if c>0 else "#FF4B4B"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

st.divider()

# --- 6. ANALYSE BEREICH ---
c1, c2 = st.columns(2)

# Ticker Auswahl (Global für beide Spalten)
s_tkr = st.selectbox("Symbol wählen:", list(TICKER_NAMES.keys()), format_func=lambda x: TICKER_NAMES.get(x,x))
d_s = get_data(s_tkr, interval="4h")

if not d_s.empty:
    cp = float(d_s['Close'].iloc[-1])
    pcp = float(d_s['Close'].iloc[-2])

    # Inputs für Kursziel & SL
    inp1, inp2 = st.columns(2)
    target_val = inp1.number_input("Kursziel:", value=float(cp*1.05), step=0.1)
    sl_val = inp2.number_input("Stop-Loss:", value=float(cp*0.97), step=0.1)
    sl_dist = ((sl_val/cp)-1)*100

    # Aktueller Status Header
    st.markdown(f"""
        <div style="background: rgba(30,144,255,0.1); padding: 15px; border-radius: 10px; border: 1px solid #1E90FF; margin-bottom: 20px; text-align: center;">
            <span style="font-size:1.2rem;">Aktuell: <b>{cp:,.2f}</b></span> | 
            <span style="font-size:1.2rem; color:#1E90FF;">Ziel: <b>{target_val:,.2f}</b> <span style="color:#FF4B4B;">({sl_dist:+.1f}% SL)</span></span>
        </div>
    """, unsafe_allow_html=True)

    with c1:
        st.subheader("🔮 Monte-Carlo Prognose")
        plt.style.use('dark_background')
        fig, ax1 = plt.subplots(figsize=(10, 7))
        fig.patch.set_facecolor('#0E1117'); ax1.set_facecolor('#0E1117')
        
        # Simulation
        log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1))
        vol = log_returns.std()
        for _ in range(30):
            p = [cp]
            for _ in range(20): p.append(p[-1] * np.exp(np.random.normal(0, vol)))
            ax1.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.2)
        
        ax1.axhline(y=cp, color='white', linestyle='--', alpha=0.5)
        ax1.axhline(y=target_val, color='#1E90FF', linestyle='-', label="Target")
        ax1.axhline(y=sl_val, color='#FF4B4B', linestyle='-', label="SL")
        st.pyplot(fig)

    with c2:
        st.subheader("📈 Historischer Chart")
        fig2, ax2 = plt.subplots(figsize=(10, 7))
        fig2.patch.set_facecolor('#0E1117'); ax2.set_facecolor('#0E1117')
        
        # Preis-Chart
        ax2.plot(d_s.index, d_s['Close'], color='#1E90FF', linewidth=2, label="Preis")
        ax2.fill_between(d_s.index, d_s['Close'], cp*0.9, color='#1E90FF', alpha=0.1)
        ax2.grid(color='gray', linestyle='--', alpha=0.2)
        st.pyplot(fig2)

    # --- OPTIONS SCANNER UNTEN ---
    st.divider()
    st.subheader("🎯 Options Scanner (Top 5 nach Open Interest)")
    calls, puts = get_options_data(s_tkr)
    
    if calls is not None:
        oc1, oc2 = st.columns(2)
        with oc1:
            st.write("🟢 **Top Calls**")
            st.dataframe(calls[['strike', 'lastPrice', 'openInterest']], use_container_width=True)
        with oc2:
            st.write("🔴 **Top Puts**")
            st.dataframe(puts[['strike', 'lastPrice', 'openInterest']], use_container_width=True)
    else:
        st.info("Für dieses Symbol sind keine Optionsdaten (US-Markt) verfügbar.")
