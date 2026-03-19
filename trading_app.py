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
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", 
    "^GDAXI": "DAX Index (DE)", "^STOXX50E": "EuroStoxx 50 (EU)", 
    "^NSEI": "Nifty 50 (IN)", "XU100.IS": "BIST 100 (TR)",
    "ADS.DE": "Adidas (DE)", "AIR.DE": "Airbus (EU)", "ALV.DE": "Allianz (DE)", "BAS.DE": "BASF (DE)", 
    "BAYN.DE": "Bayer (DE)", "BEI.DE": "Beiersdorf (DE)", "BMW.DE": "BMW (DE)", "BNR.DE": "Brenntag (DE)", 
    "CBK.DE": "Commerzbank (DE)", "CON.DE": "Continental (DE)", "1COV.DE": "Covestro (DE)", 
    "DTG.DE": "Daimler Truck (DE)", "DBK.DE": "Deutsche Bank (DE)", "DB1.DE": "Deutsche Börse (DE)", 
    "DHL.DE": "DHL Group (DE)", "DTE.DE": "Telekom (DE)", "EON.DE": "E.ON (DE)", 
    "FME.DE": "Fresenius Med. (DE)", "FRE.DE": "Fresenius SE (DE)", "GEA.DE": "GEA Group (DE)", 
    "HNR1.DE": "Hannover Rück (DE)", "HEI.DE": "Heidelberg Mat. (DE)", "HEN3.DE": "Henkel (DE)", 
    "IFX.DE": "Infineon (DE)", "MBG.DE": "Mercedes-Benz (DE)", "MRK.DE": "Merck (DE)", 
    "MTX.DE": "MTU Aero (DE)", "MUV2.DE": "Münchener Rück (DE)", "PAH3.DE": "Porsche SE (DE)", 
    "PUM.DE": "Puma (DE)", "QIA.DE": "Qiagen (NL/DE)", "RHM.DE": "Rheinmetall (DE)", 
    "RWE.DE": "RWE (DE)", "SAP.DE": "SAP (DE)", "SIE.DE": "Siemens (DE)", 
    "ENR.DE": "Siemens Energy (DE)", "SHL.DE": "Siemens Health. (DE)", "SY1.DE": "Symrise (DE)", 
    "VOW3.DE": "Volkswagen (DE)", "VNA.DE": "Vonovia (DE)", "ZAL.DE": "Zalando (DE)",
    "AAPL": "Apple (US)", "MSFT": "Microsoft (US)", "NVDA": "Nvidia (US)", "AMZN": "Amazon (US)", 
    "GOOGL": "Alphabet (US)", "META": "Meta (US)", "TSLA": "Tesla (US)", "AVGO": "Broadcom (US)", 
    "COST": "Costco (US)", "NFLX": "Netflix (US)", "AMD": "AMD (US)", "ADBE": "Adobe (US)", 
    "PEP": "PepsiCo (US)", "CSCO": "Cisco (US)", "INTC": "Intel (US)", "TMUS": "T-Mobile US (US)", 
    "INTU": "Intuit (US)", "AMGN": "Amgen (US)", "QCOM": "Qualcomm (US)", "ISRG": "Intuitive Surg. (US)",
    "THYAO.IS": "Turkish Airlines (TR)", "ASELS.IS": "Aselsan (TR)", "KCHOL.IS": "Koc Holding (TR)",
    "RELIANCE.NS": "Reliance Ind. (IN)", "TCS.NS": "TCS (IN)", "HDFCBANK.NS": "HDFC Bank (IN)"
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; background-image: linear-gradient(180deg, #0e1525 0%, #050a14 100%); color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(8px); margin-bottom: 10px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; color: #FFFFFF; font-family: 'Courier New', monospace; }
    .news-container { height: 350px; overflow: hidden; position: relative; border-left: 2px solid #1E90FF; padding-left: 12px; }
    .news-scroll { animation: scroll-up 45s linear infinite; }
    .news-item { margin-bottom: 12px; font-size: 0.85rem; background: rgba(255,255,255,0.05); padding: 8px; border-radius: 8px; }
    @keyframes scroll-up { 0% { transform: translateY(0); } 100% { transform: translateY(-50%); } }
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

def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- 5. MARKT-FRAMEWORK ---
st.title("🚀 Bio-Trading Monitor Live PRO")
st.caption(f"Letztes Update: {pd.Timestamp.now().strftime('%H:%M:%S')} | Auto-Refresh: 60s")

# Währungen & Indizes (wie gehabt)
st.subheader("💱 Währungen & 📈 Indizes")
c_m1, c_m2, c_m3, c_m4, c_m5, c_m6 = st.columns(6)
m_symbols = ["EURUSD=X", "EURRUB=X", "^GDAXI", "^STOXX50E", "^NSEI", "XU100.IS"]
cols = [c_m1, c_m2, c_m3, c_m4, c_m5, c_m6]

for i, t in enumerate(m_symbols):
    df_m = get_data(t, period="5d")
    if not df_m.empty:
        l = float(df_m['Close'].iloc[-1])
        c = ((l / df_m['Close'].iloc[-2]) - 1) * 100
        cols[i].markdown(f'<div class="market-card"><div style="font-size:0.7rem; color:#8892b0;">{TICKER_NAMES.get(t,t)}</div>'
                        f'<div class="metric-value">{l:,.2f}</div>'
                        f'<div style="color:{"#00FFA3" if c>0 else "#FF4B4B"}; font-size:0.8rem;">{c:+.2f}%</div></div>', unsafe_allow_html=True)

# --- 6. DEEP-DIVE ANALYSE ---
st.divider()
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📊 Deep-Dive Chart & Analyse")
    ca, cb = st.columns(2)
    s_idx = ca.selectbox("Markt wählen:", ["DAX 40 (DE)", "NASDAQ 100 (US)", "BIST 100 (TR)", "Nifty 50 (IN)"])
    STOCKS_DICT = {
        "DAX 40 (DE)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
        "NASDAQ 100 (US)": [k for k in TICKER_NAMES.keys() if not k.endswith(".DE") and not k.endswith(".IS") and not k.endswith(".NS") and not "=" in k and not "^" in k],
        "BIST 100 (TR)": ["THYAO.IS", "ASELS.IS", "KCHOL.IS"],
        "Nifty 50 (IN)": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    }
    s_tkr = cb.selectbox("Aktie wählen:", STOCKS_DICT[s_idx], format_func=lambda x: TICKER_NAMES.get(x,x))
    
    d_s = get_data(s_tkr, interval="4h")
    if not d_s.empty:
        cp = float(d_s['Close'].iloc[-1])
        pcp = float(d_s['Close'].iloc[-2])
        
        # --- NEU: EINGABE FÜR TARGET & SL ---
        cc1, cc2 = st.columns(2)
        target_input = cc1.number_input("Dein Kursziel:", value=float(cp * 1.10), step=0.1)
        sl_input = cc2.number_input("Dein Stop-Loss (SL):", value=float(cp * 0.95), step=0.1)
        
        sl_dist = ((sl_input / cp) - 1) * 100
        
        # --- NEU: AKTUELLE WERTE ANZEIGE ---
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; background: rgba(30,144,255,0.1); padding: 15px; border-radius: 10px; border: 1px solid #1E90FF; margin-bottom: 20px;">
                <div>
                    <small style="color:#8892b0;">Aktueller Kurs</small><br>
                    <span style="font-size:1.8rem; font-weight:bold; color:white;">{cp:,.2f}</span>
                    <span style="color:{"#00FFA3" if cp>pcp else "#FF4B4B"}; margin-left:10px;">{((cp/pcp)-1)*100:+.2f}%</span>
                </div>
                <div style="text-align: right;">
                    <small style="color:#8892b0;">Ziel (Abstand zum SL)</small><br>
                    <span style="font-size:1.8rem; font-weight:bold; color:#1E90FF;">{target_input:,.2f}</span>
                    <span style="color:#FF4B4B; margin-left:10px; font-size:1.1rem;">({sl_dist:+.1f}% SL)</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Monte Carlo & Plot
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [3, 1]})
        fig.patch.set_facecolor('#0E1117')
        ax1.set_facecolor('#0E1117')
        
        log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1))
        vol = log_returns.std()
        ends = []
        for _ in range(40):
            p = [cp]
            for _ in range(30): p.append(p[-1] * np.exp(np.random.normal(0, vol)))
            ax1.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.15)
            ends.append(p[-1])
        
        ax1.axhline(y=cp, color='white', linestyle='--', alpha=0.3)
        ax1.axhline(y=target_input, color='#1E90FF', linestyle=':', label="Target")
        ax1.axhline(y=sl_input, color='#FF4B4B', linestyle=':', label="SL")
        ax1.set_title(f"Simulation: {TICKER_NAMES.get(s_tkr, s_tkr)}")

        ax2.set_facecolor('#0E1117')
        rsi = calculate_rsi(d_s['Close'])
        ax2.plot(rsi.values, color='#1E90FF')
        ax2.axhline(y=70, color='#FF4B4B', alpha=0.3); ax2.axhline(y=30, color='#00FFA3', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)

with c2:
    st.subheader("🗞️ Live News")
    s_obj = yf.Ticker(s_tkr)
    n_list = s_obj.news
    if n_list:
        news_items = ""
        for n in n_list[:8]:
            title = n.get('title', '')
            link = n.get('link', '#')
            news_items += f'<div class="news-item"><a href="{link}" target="_blank" style="color:#1E90FF; text-decoration:none;">{title[:80]}...</a></div>'
        
        st.markdown(f'<div class="news-container"><div class="news-scroll">{news_items}{news_items}</div></div>', unsafe_allow_html=True)
