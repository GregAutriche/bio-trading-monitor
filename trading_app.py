import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. VOLLSTÄNDIGES NAMENS-MAPPING (KLARTEXT) ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50",
    "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    # DAX 40 (Auszug)
    "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer",
    "BMW.DE": "BMW", "DBK.DE": "Deutsche Bank", "DTE.DE": "Telekom", "SAP.DE": "SAP", "SIE.DE": "Siemens",
    # EuroStoxx 50 (Auszug)
    "AIR.PA": "Airbus (FR)", "MC.PA": "LVMH", "OR.PA": "L'Oréal", "ASML.AS": "ASML", "SAN.PA": "Sanofi",
    "TTE.PA": "TotalEnergies", "BNP.PA": "BNP Paribas", "ITX.MC": "Inditex",
    # NASDAQ
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "TSLA": "Tesla", "AMZN": "Amazon", "META": "Meta",
    # BIST / Nifty
    "THYAO.IS": "Turkish Airlines", "RELIANCE.NS": "Reliance Ind.", "TCS.NS": "TCS"
}

TICKER_GROUPS = {
    "DAX 40 (DE)": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "ADS.DE", "BMW.DE", "BAYN.DE", "BAS.DE", "DBK.DE", "RHM.DE"],
    "EuroStoxx 50 (EU)": ["AIR.PA", "MC.PA", "OR.PA", "ASML.AS", "SAN.PA", "BNP.PA", "TTE.PA", "ITX.MC"],
    "NASDAQ 100 (US)": ["AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "AMZN": "Amazon", "GOOGL": "Alphabet A", "GOOG": "Alphabet C", "META": "Meta (FB)", "TSLA": "Tesla", 
    "AVGO": "Broadcom", "COST": "Costco", "NFLX": "Netflix", "AMD": "AMD", "ADBE": "Adobe", "PEP": "PepsiCo", "CSCO": "Cisco", "TMUS": "T-Mobile US", 
    "AVGO": "Broadcom", "QCOM": "Qualcomm", "INTC": "Intel", "INTU": "Intuit", "AMGN": "Amgen", "ISRG": "Intuitive Surg.", "TXN": "Texas Instr.", "HON": "Honeywell", 
    "AMAT": "Applied Mat.", "BKNG": "Booking Holdings", "VRTX": "Vertex Pharm.", "SBUX": "Starbucks", "PANW": "Palo Alto Networks", "GILD": "Gilead Sciences", 
    "SNPS": "Synopsys", "REGN": "Regeneron", "MDLZ": "Mondelez", "PYPL": "PayPal", "ADI": "Analog Devices", "MU": "Micron Tech", "KLAC": "KLA Corp", "LRCX": "Lam Research"],
    "BIST 100 (TR)": ["THYAO.IS", "ASELS.IS", "KCHOL.IS", "TUPRS.IS"],
    "Nifty 50 (IN)": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]
}

# --- 3. DESIGN (DARK MODE & AKTIIONSFARBEN) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; color: white; }
    .bullish { color: #00FFA3; font-weight: bold; }
    .bearish { color: #FF4B4B; font-weight: bold; }
    .header-box { background: rgba(30,144,255,0.1); padding: 15px; border-radius: 12px; border: 1px solid #1E90FF; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN (DATEN & SCANNER) ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="4h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def run_market_scanner(ticker_list):
    """Scannt die Top 5 Call/Put Signale basierend auf dem Trend"""
    results = []
    for t in ticker_list:
        df = get_data(t, period="5d")
        if not df.empty:
            cp = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            trend = ((cp / prev) - 1) * 100
            results.append({"Titel": TICKER_NAMES.get(t, t), "Kurs": round(cp, 2), "Trend %": round(trend, 2)})
    return pd.DataFrame(results)

# --- 5. HEADER: ZEILE 1 (WÄHRUNGEN) & ZEILE 2 (INDIZES) ---
st.title("🚀 Bio-Trading Monitor Live PRO")

st.subheader("💱 Währungen")
cf1, cf2, cf3 = st.columns(3)
for i, t in enumerate(["EURUSD=X", "EURRUB=X"]):
    df_f = get_data(t, period="2d")
    if not df_f.empty:
        l = float(df_f['Close'].iloc[-1]); c = ((l/df_f['Close'].iloc[-2])-1)*100
        (cf1 if i==0 else cf2).markdown(f'<div class="market-card"><small>{TICKER_NAMES[t]}</small><br><span class="metric-value">{l:,.5f}</span> <span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

st.subheader("📈 Markt-Indizes")
cols_i = st.columns(5)
for i, t in enumerate(["^GDAXI", "^STOXX50E", "^NDX", "XU100.IS", "^NSEI"]):
    df_i = get_data(t, period="2d")
    if not df_i.empty:
        l = float(df_i['Close'].iloc[-1]); c = ((l/df_i['Close'].iloc[-2])-1)*100
        cols_i[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.2f}</span> <span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

# --- 6. HAUPTBEREICH: DEEP-DIVE & SCANNER ---
st.divider()
ca, cb = st.columns(2)
market_sel = ca.selectbox("Markt wählen:", list(TICKER_GROUPS.keys()))
stock_sel = cb.selectbox("Aktie für Detail-Analyse:", TICKER_GROUPS[market_sel], format_func=lambda x: TICKER_NAMES.get(x,x))

d_s = get_data(stock_sel)
if not d_s.empty:
    cp = float(d_s['Close'].iloc[-1])
    # Wetter-Logik Anzeige oben
    st.markdown(f'<div class="header-box"><span style="font-size:1.3rem;">Fokus: <b>{TICKER_NAMES.get(stock_sel, stock_sel)}</b></span> | <span style="font-size:1.3rem;">Kurs: <b>{cp:,.2f}</b></span> | <span style="color:#00FFA3;">Ziel (Bio): {cp*1.05:,.2f}</span></div>', unsafe_allow_html=True)

    cl, cr = st.columns([1.4, 1])

    with cl:
        st.subheader("🔮 Prognose-Wetter (Monte Carlo)")
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 5.5)); fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
        log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)); vol = log_returns.std()
        for _ in range(25):
            p = [cp]
            for _ in range(20): p.append(p[-1] * np.exp(np.random.normal(0, vol)))
            ax.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.15)
        ax.axhline(y=cp, color='white', linestyle='--', alpha=0.3)
        st.pyplot(fig)

    with cr:
        st.subheader(f"🎯 Scanner: {market_sel}")
        with st.spinner("Scanne Markt-Signale..."):
            scan_results = run_market_scanner(TICKER_GROUPS[market_sel])
            
            # TOP 5 CALLS
            st.markdown("<span class='bullish'>🟢 TOP 5 CALL-SIGNALE (Momentum)</span>", unsafe_allow_html=True)
            top_calls = scan_results.sort_values(by="Trend %", ascending=False).head(5)
            st.dataframe(top_calls, use_container_width=True, hide_index=True)
            
            st.write("") # Abstand
            
            # TOP 5 PUTS
            st.markdown("<span class='bearish'>🔴 TOP 5 PUT-SIGNALE (Risiko)</span>", unsafe_allow_html=True)
            top_puts = scan_results.sort_values(by="Trend %", ascending=True).head(5)
            st.dataframe(top_puts, use_container_width=True, hide_index=True)

# --- 7. STATUS BAR ---
st.info(f"Bio-Trading Status: {'BULLISH ☀️' if d_s['Close'].iloc[-1] > d_s['Close'].iloc[-5] else 'BEARISH ⛈️'} | Analyse-Basis: 4h Intervalle")
