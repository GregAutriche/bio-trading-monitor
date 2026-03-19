import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION & REFRESH ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. ERWEITERTES NAMENS-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB",
    "^GDAXI": "DAX 40 (DE)", "^STOXX50E": "EuroStoxx 50 (EU)", "^NDX": "NASDAQ 100 (US)", 
    "XU100.IS": "BIST 100 (TR)", "^NSEI": "Nifty 50 (IN)",
    "SAP.DE": "SAP", "SIE.DE": "Siemens", "ALV.DE": "Allianz", "DTE.DE": "Telekom", "AIR.DE": "Airbus",
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "TSLA": "Tesla", "AMD": "AMD",
    "THYAO.IS": "Turkish Airlines", "ASELS.IS": "Aselsan", "RELIANCE.NS": "Reliance"
}

# --- 3. DESIGN (DARK MODE & CARDS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; color: #FFFFFF; font-family: 'Courier New', monospace; }
    h1, h2, h3 { color: #FFFFFF !important; }
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

# --- 5. HEADER: ZEILE 1 (WÄHRUNGEN) & ZEILE 2 (INDIZES) ---
st.title("🚀 Bio-Trading Monitor Live PRO")

st.subheader("💱 Währungen")
cols_f = st.columns(6)
for i, t in enumerate(["EURUSD=X", "EURRUB=X"]):
    df = get_data(t, period="5d")
    if not df.empty:
        l = float(df['Close'].iloc[-1]); c = ((l/df['Close'].iloc[-2])-1)*100
        cols_f[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES[t]}</small><br><div class="metric-value">{l:,.5f}</div><span style="color:{"#00FFA3" if c>0 else "#FF4B4B"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

st.subheader("📈 Markt-Indizes")
cols_i = st.columns(5)
for i, t in enumerate(["^GDAXI", "^STOXX50E", "^NDX", "XU100.IS", "^NSEI"]):
    df = get_data(t, period="5d")
    if not df.empty:
        l = float(df['Close'].iloc[-1]); c = ((l/df['Close'].iloc[-2])-1)*100
        cols_i[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><div class="metric-value">{l:,.2f}</div><span style="color:{"#00FFA3" if c>0 else "#FF4B4B"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

# --- 6. HAUPTBEREICH: MONTE CARLO & BEWERTUNGSSYSTEM ---
st.divider()
c1, c2 = st.columns([2, 1]) # Linke Spalte breiter für den Chart

with c1:
    st.subheader("📊 Deep-Dive: Monte-Carlo Prognose")
    ca, cb = st.columns(2)
    m_choice = ca.selectbox("Markt:", ["DAX 40 (DE)", "NASDAQ 100 (US)", "BIST 100 (TR)", "Nifty 50 (IN)"])
    
    MAPPING = {
        "DAX 40 (DE)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
        "NASDAQ 100 (US)": ["AAPL", "MSFT", "NVDA", "TSLA", "AMD"],
        "BIST 100 (TR)": ["THYAO.IS", "ASELS.IS"],
        "Nifty 50 (IN)": ["RELIANCE.NS"]
    }
    s_tkr = cb.selectbox("Wert:", MAPPING[m_choice], format_func=lambda x: TICKER_NAMES.get(x,x))
    
    d_s = get_data(s_tkr)
    if not d_s.empty:
        cp = float(d_s['Close'].iloc[-1])
        # Berechnung Ziel/SL (fest ohne Regler)
        target = cp * 1.05; sl = cp * 0.97; sl_pct = ((sl/cp)-1)*100
        
        st.markdown(f'<div style="background:rgba(30,144,255,0.1); padding:10px; border-radius:10px; border:1px solid #1E90FF; text-align:center;">'
                    f'<b>{TICKER_NAMES.get(s_tkr,s_tkr)}</b>: {cp:,.2f} | <span style="color:#1E90FF;">Ziel: {target:,.2f}</span> '
                    f'<span style="color:#FF4B4B;">(SL: {sl_pct:+.1f}%)</span></div>', unsafe_allow_html=True)

        # Plot
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 5)); fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
        log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)); vol = log_returns.std()
        for _ in range(30):
            p = [cp]
            for _ in range(25): p.append(p[-1] * np.exp(np.random.normal(0, vol)))
            ax.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.15)
        ax.axhline(y=cp, color='white', linestyle='--', alpha=0.3)
        ax.axhline(y=target, color='#1E90FF', alpha=0.8, label="Target")
        ax.axhline(y=sl, color='#FF4B4B', alpha=0.8, label="SL")
        st.pyplot(fig)

with c2:
    st.subheader("🎯 Top 5 Signale")
    # Simuliertes Bewertungssystem
    signals = []
    for t in MAPPING[m_choice]:
        df_sig = get_data(t, period="20d")
        if not df_sig.empty:
            score = ((df_sig['Close'].iloc[-1] / df_sig['Close'].iloc[-5]) - 1) * 100
            signals.append({"Titel": TICKER_NAMES.get(t,t), "Kurs": f"{df_sig['Close'].iloc[-1]:,.2f}", "Score": round(score, 2)})
    
    if signals:
        sig_df = pd.DataFrame(signals).sort_values(by="Score", ascending=False).head(5)
        st.table(sig_df) # Saubere Tabelle ohne Index
    else:
        st.write("Warte auf Daten...")

st.caption("Auto-Refresh aktiv. Alle Preise basieren auf 4h-Intervallen.")
