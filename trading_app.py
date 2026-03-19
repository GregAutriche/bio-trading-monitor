import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. NAMENS-MAPPING (INKL. EUR/RUB) ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", 
    "EURRUB=X": "EUR/RUB", 
    "^GDAXI": "DAX Index", 
    "^STOXX50E": "EuroStoxx 50",
    "AAPL": "Apple (US)", 
    "NVDA": "Nvidia (US)", 
    "TSLA": "Tesla (US)", 
    "SAP.DE": "SAP (DE)", 
    "ADS.DE": "Adidas (DE)", 
    "DBK.DE": "Deutsche Bank (DE)"
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; color: white; font-family: 'Courier New', monospace; }
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

# --- 5. DASHBOARD HEADER (QUICKVIEW) ---
st.title("🚀 Bio-Trading Monitor Live PRO")
# ZEILE 1: WÄHRUNGEN (FOREX)
st.subheader("💱 Währungen")
forex_symbols = ["EURUSD=X", "EURRUB=X"]
cols_f = st.columns(len(forex_symbols) + 4) # +4 leere Spalten, damit sie links bündig bleiben

for i, t in enumerate(forex_symbols):
    df_m = get_data(t, period="5d")
    if not df_m.empty:
        l = float(df_m['Close'].iloc[-1])
        c = ((l / df_m['Close'].iloc[-2]) - 1) * 100
        cols_f[i].markdown(f'''
            <div class="market-card">
                <small>{TICKER_NAMES.get(t,t)}</small><br>
                <div class="metric-value">{l:,.5f}</div>
                <span style="color:{"#00FFA3" if c>0 else "#FF4B4B"}">{c:+.2f}%</span>
            </div>''', unsafe_allow_html=True)

# ZEILE 2: INDIZES & AKTIEN
st.subheader("📈 Märkte & Aktien")
market_symbols = ["^GDAXI", "^STOXX50E", "AAPL", "SAP.DE"]
cols_m = st.columns(len(market_symbols) + 2) # +2 leere Spalten für die Optik

for i, t in enumerate(market_symbols):
    df_m = get_data(t, period="5d")
    if not df_m.empty:
        l = float(df_m['Close'].iloc[-1])
        c = ((l / df_m['Close'].iloc[-2]) - 1) * 100
        cols_m[i].markdown(f'''
            <div class="market-card">
                <small>{TICKER_NAMES.get(t,t)}</small><br>
                <div class="metric-value">{l:,.2f}</div>
                <span style="color:{"#00FFA3" if c>0 else "#FF4B4B"}">{c:+.2f}%</span>
            </div>''', unsafe_allow_html=True)

# --- 6. DEEP-DIVE ANALYSE (OPTIMIERT) ---
# Marktauswahl -> Aktienauswahl
ca, cb = st.columns(2)
s_idx = ca.selectbox("Markt wählen:", ["DAX 40 (DE)", "NASDAQ 100 (US)", "BIST 100 (TR)", "Nifty 50 (IN)"])
STOCKS_DICT = {
    "DAX 40 (DE)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
    "NASDAQ 100 (US)": [k for k in TICKER_NAMES.keys() if not k.endswith(".DE") and not k.endswith(".IS") and not k.endswith(".NS") and not "=" in k and not "^" in k],
    "BIST 100 (TR)": ["THYAO.IS", "ASELS.IS", "KCHOL.IS"],
    "Nifty 50 (IN)": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
}
s_tkr = cb.selectbox("Wert wählen:", STOCKS_DICT[s_idx], format_func=lambda x: TICKER_NAMES.get(x,x))

d_s = get_data(s_tkr, interval="4h")
if not d_s.empty:
    cp = float(d_s['Close'].iloc[-1])
    is_forex = "=X" in s_tkr
    
    # --- LOGIK FÜR FESTE WERTE (KEINE REGLER) ---
    # Wir berechnen das Ziel (z.B. +5%) und den SL (z.B. -3%) automatisch
    target_val = cp * 1.05
    sl_val = cp * 0.97
    sl_dist = ((sl_val/cp)-1)*100

    # Formatierung vorab festlegen, um den f-String Fehler zu vermeiden
    fmt = ",.5f" if is_forex else ",.2f"
    cp_str = format(cp, fmt)
    target_str = format(target_val, fmt)

    # Status Header ohne Eingabefelder
    st.markdown(f"""
        <div style="background: rgba(30,144,255,0.1); padding: 20px; border-radius: 12px; border: 1px solid #1E90FF; text-align: center;">
            <div style="color:#8892b0; font-size:0.9rem; margin-bottom:5px;">{TICKER_NAMES.get(s_tkr, s_tkr)} Status</div>
            <span style="font-size:1.6rem; font-weight:bold;">Aktuell: {cp_str}</span>
            <span style="margin: 0 20px; color:#1E90FF; font-size:1.4rem;">|</span>
            <span style="font-size:1.6rem; font-weight:bold; color:#1E90FF;">Ziel: {target_str}</span>
            <div style="color:#FF4B4B; font-size:1rem; margin-top:5px;">🛡️ Stop-Loss Abstand: {sl_dist:+.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

    # Charts in zwei Spalten darunter
    c1, c2 = st.columns(2)
    # ... hier dein Plot-Code für c1 (Monte Carlo) und c2 (Historisch) ...


    # ... hier folgen dann die Charts in c1 und c2 ...

    with c1:
        st.subheader("🔮 Monte-Carlo Prognose")
        plt.style.use('dark_background')
        fig, ax1 = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#0E1117'); ax1.set_facecolor('#0E1117')
        
        log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1))
        vol = log_returns.std()
        for _ in range(25):
            p = [cp]
            for _ in range(30): p.append(p[-1] * np.exp(np.random.normal(0, vol)))
            ax1.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.15)
        
        ax1.axhline(y=cp, color='white', linestyle='--', alpha=0.5)
        ax1.axhline(y=target_val, color='#1E90FF', label="Target")
        ax1.axhline(y=sl_val, color='#FF4B4B', label="SL")
        st.pyplot(fig)

    with c2:
        st.subheader("📈 Historischer Verlauf (4h)")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        fig2.patch.set_facecolor('#0E1117'); ax2.set_facecolor('#0E1117')
        ax2.plot(d_s.index, d_s['Close'], color='#1E90FF', linewidth=2)
        ax2.fill_between(d_s.index, d_s['Close'], cp*0.98 if is_forex else cp*0.9, color='#1E90FF', alpha=0.1)
        ax2.grid(alpha=0.1)
        st.pyplot(fig2)

    # # --- OPTIONS SCANNER MIT TITEL-FIX ---
st.divider()

# Wir rufen hier die Expiration-Daten ab, um sie im Titel zu zeigen
tk_obj = yf.Ticker(s_tkr)
next_expiry = tk_obj.options[0] if tk_obj.options else "N/A"

st.subheader(f"🎯 Options Scanner: {TICKER_NAMES.get(s_tkr, s_tkr)}")
st.caption(f"Top 5 nach Open Interest | Nächstes Verfallsdatum: {next_expiry}")

calls, puts = get_options_data(s_tkr)

if calls is not None:
    oc1, oc2 = st.columns(2)
    with oc1:
        st.markdown("### 🟢 Top Calls")
        # Wir blenden den Index (0,1,2..) aus für eine sauberere Ansicht
        st.dataframe(calls[['strike', 'lastPrice', 'openInterest']].reset_index(drop=True), use_container_width=True)
    with oc2:
        st.markdown("### 🔴 Top Puts")
        st.dataframe(puts[['strike', 'lastPrice', 'openInterest']].reset_index(drop=True), use_container_width=True)
else:
    st.info(f"Für {TICKER_NAMES.get(s_tkr, s_tkr)} sind aktuell keine Optionsdaten verfügbar.")
