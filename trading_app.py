import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. NAMENS-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB",
    "^GDAXI": "DAX 40 (DE)", "^STOXX50E": "EuroStoxx 50 (EU)", "^NDX": "NASDAQ 100 (US)",
    "AAPL": "Apple", "NVDA": "Nvidia", "TSLA": "Tesla", "SAP.DE": "SAP", "ADS.DE": "Adidas"
}

# --- 3. DESIGN & AKTIIONSFARBEN (WETTER-LOGIK) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; }
    /* Wetter-Farben */
    .bullish-green { color: #00FFA3; font-weight: bold; }
    .bearish-red { color: #FF4B4B; font-weight: bold; }
    .neutral-blue { color: #1E90FF; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="4h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def get_options_logic(ticker_str):
    """Holt die Top 5 Calls/Puts nach Open Interest"""
    try:
        tk = yf.Ticker(ticker_str)
        if not tk.options: return None, None
        opt = tk.option_chain(tk.options[0])
        calls = opt.calls.sort_values("openInterest", ascending=False).head(5)
        puts = opt.puts.sort_values("openInterest", ascending=False).head(5)
        return calls[['strike', 'openInterest']], puts[['strike', 'openInterest']]
    except: return None, None

# --- 5. HEADER (ZEILE 1 & 2) ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# Zeile 1: Währungen (5 Stellen)
st.subheader("💱 Währungen")
c1, c2, _ = st.columns([1,1,4])
for i, t in enumerate(["EURUSD=X", "EURRUB=X"]):
    df = get_data(t, period="2d")
    if not df.empty:
        l = float(df['Close'].iloc[-1]); c = ((l/df['Close'].iloc[-2])-1)*100
        color = "bullish-green" if c > 0 else "bearish-red"
        (c1 if i==0 else c2).markdown(f'<div class="market-card"><small>{TICKER_NAMES[t]}</small><br><span class="metric-value">{l:,.5f}</span> <span class="{color}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

# Zeile 2: Indizes
st.subheader("📈 Markt-Indizes")
cols_i = st.columns(5)
for i, t in enumerate(["^GDAXI", "^STOXX50E", "^NDX"]):
    df = get_data(t, period="2d")
    if not df.empty:
        l = float(df['Close'].iloc[-1]); c = ((l/df['Close'].iloc[-2])-1)*100
        color = "bullish-green" if c > 0 else "bearish-red"
        cols_i[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES[t]}</small><br><span class="metric-value">{l:,.2f}</span> <span class="{color}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

st.divider()

# --- 6. HAUPTBEREICH (MONTE CARLO & OPTIONS-WETTER) ---
col_main, col_side = st.columns([2, 1])

# Auswahl (oben drüber)
s_tkr = st.selectbox("Analyse-Wert:", ["NVDA", "AAPL", "TSLA", "SAP.DE"], format_func=lambda x: TICKER_NAMES.get(x,x))
d_s = get_data(s_tkr)

if not d_s.empty:
    cp = float(d_s['Close'].iloc[-1])
    
    with col_main:
        st.subheader("🔮 Prognose-Wetter (Monte Carlo)")
        # Monte Carlo Plot
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 5)); fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
        log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)); vol = log_returns.std()
        for _ in range(25):
            p = [cp]
            for _ in range(20): p.append(p[-1] * np.exp(np.random.normal(0, vol)))
            ax.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.2)
        ax.axhline(y=cp, color='white', linestyle='--', alpha=0.5)
        st.pyplot(fig)

    with col_side:
        st.subheader("🎯 Top 5 Call / Put")
        calls, puts = get_options_logic(s_tkr)
        
        if calls is not None:
            # Wetter-Logik Anzeige
            st.markdown(f"**Aktueller Kurs: {cp:,.2f}**")
            
            st.markdown("<span class='bullish-green'>🟢 TOP CALLS (Widerstand)</span>", unsafe_allow_html=True)
            st.dataframe(calls.reset_index(drop=True), use_container_width=True)
            
            st.markdown("<span class='bearish-red'>🔴 TOP PUTS (Unterstützung)</span>", unsafe_allow_html=True)
            st.dataframe(puts.reset_index(drop=True), use_container_width=True)
        else:
            st.warning("Keine Options-Daten für dieses Symbol (nur US-Werte).")

# --- 7. STATUS BAR ---
st.info(f"Bio-Trading Status: {'BULLISH ☀️' if d_s['Close'].iloc[-1] > d_s['Close'].iloc[-5] else 'BEARISH ⛈️'} | Update: {pd.Timestamp.now().strftime('%H:%M:%S')}")
