import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-GRUPPEN (VOLLSTÄNDIG) ---
TICKER_GROUPS = {
    "DAX 40 (DE)": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "MBG.DE", "BMW.DE", "BAS.DE", "BAYN.DE", "ADS.DE", "RHM.DE", "DBK.DE"],
    "EuroStoxx 50 (EU)": ["ASML.AS", "MC.PA", "OR.PA", "TTE.PA", "SAN.PA", "SAP.DE", "SIE.DE", "AIR.PA", "BNP.PA"],
    "NASDAQ 100 (US)": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "COST", "NFLX", "AMD"],
    "BIST 100 (TR)": ["THYAO.IS", "ASELS.IS", "KCHOL.IS", "TUPRS.IS", "BIMAS.IS", "AKBNK.IS"],
    "Nifty 50 (IN)": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS"]
}

TICKER_NAMES = {"EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50", "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50"}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; color: white; }
    .bullish { color: #00FFA3; font-weight: bold; }
    .bearish { color: #FF4B4B; font-weight: bold; }
    .header-box { background: rgba(30,144,255,0.1); padding: 15px; border-radius: 10px; border: 1px solid #1E90FF; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN (WETTER-LOGIK) ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="4h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def calculate_bio_options(current_price, df):
    """Berechnet synthetische Call/Put Levels basierend auf Volatilität (funktioniert global)"""
    returns = np.log(df['Close'] / df['Close'].shift(1))
    std = returns.std()
    
    calls = []
    puts = []
    # Wir erstellen 5 Levels basierend auf Standardabweichungen (Wetter-Logik)
    for i in range(1, 6):
        calls.append({"Strike": current_price * (1 + (std * i)), "Prob.": f"{100-(i*10):.0f}%"})
        puts.append({"Strike": current_price * (1 - (std * i)), "Prob.": f"{100-(i*10):.0f}%"})
        
    return pd.DataFrame(calls), pd.DataFrame(puts)

# --- 5. HEADER ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# Zeile 1: Währungen
st.subheader("💱 Währungen")
cf1, cf2, _ = st.columns([1,1,4])
for i, t in enumerate(["EURUSD=X", "EURRUB=X"]):
    df_f = get_data(t, period="2d")
    if not df_f.empty:
        l = float(df_f['Close'].iloc[-1]); c = ((l/df_f['Close'].iloc[-2])-1)*100
        (cf1 if i==0 else cf2).markdown(f'<div class="market-card"><small>{TICKER_NAMES[t]}</small><br><span class="metric-value">{l:,.5f}</span> <span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

# Zeile 2: Indizes
st.subheader("📈 Markt-Indizes")
cols_i = st.columns(5)
for i, t in enumerate(["^GDAXI", "^STOXX50E", "^NDX", "XU100.IS", "^NSEI"]):
    df_i = get_data(t, period="2d")
    if not df_i.empty:
        l = float(df_i['Close'].iloc[-1]); c = ((l/df_i['Close'].iloc[-2])-1)*100
        cols_i[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.2f}</span> <span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

# --- 6. DEEP-DIVE ---
st.divider()
ca, cb = st.columns(2)
market_sel = ca.selectbox("Markt wählen:", list(TICKER_GROUPS.keys()))
stock_sel = cb.selectbox("Aktie wählen:", TICKER_GROUPS[market_sel])

d_s = get_data(stock_sel)
if not d_s.empty:
    cp = float(d_s['Close'].iloc[-1])
    
    # Wetter-Logik Header
    st.markdown(f"""<div class="header-box">
        <span style="font-size:1.3rem;">Status: <b>{stock_sel}</b></span> | 
        <span style="font-size:1.3rem;">Kurs: <b>{cp:,.2f}</b></span> | 
        <span style="color:#00FFA3;">Ziel (Bio): {cp*1.05:,.2f}</span>
    </div>""", unsafe_allow_html=True)

    c_left, c_right = st.columns([1.5, 1])

    with c_left:
        st.subheader("🔮 Bio-Prognose (Monte Carlo)")
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 5)); fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
        log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)); vol = log_returns.std()
        for _ in range(30):
            p = [cp]
            for _ in range(25): p.append(p[-1] * np.exp(np.random.normal(0, vol)))
            ax.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.15)
        ax.axhline(y=cp, color='white', linestyle='--', alpha=0.3)
        st.pyplot(fig)

    with c_right:
        st.subheader("🎯 Top 5 Call / Put (Bio-Levels)")
        calls, puts = calculate_bio_options(cp, d_s)
        
        st.markdown("<span class='bullish'>🟢 TOP CALLS (Widerstand)</span>", unsafe_allow_html=True)
        st.dataframe(calls, use_container_width=True, hide_index=True)
        
        st.markdown("<span class='bearish'>🔴 TOP PUTS (Support)</span>", unsafe_allow_html=True)
        st.dataframe(puts, use_container_width=True, hide_index=True)

# --- 7. FOOTER ---
st.info(f"Bio-Trading Algorithmus aktiv | Markt: {market_sel} | Letzter Check: {pd.Timestamp.now().strftime('%H:%M:%S')}")
