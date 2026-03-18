import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. NAMENS-MAPPING MIT LÄNDER-KÜRZELN ---
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
st.caption(f"Letztes Daten-Update: {pd.Timestamp.now().strftime('%H:%M:%S')} | Auto-Refresh: 60s")

st.subheader("💱 Währungen (Forex) 💱")
SYMBOLS_FX = ["EURUSD=X", "EURRUB=X"]
cols_fx = st.columns(len(SYMBOLS_FX))
for i, t in enumerate(SYMBOLS_FX):
    df = get_data(t, period="5d")
    if not df.empty:
        last = float(df['Close'].iloc[-1]); chg = ((last / df['Close'].iloc[-2]) - 1) * 100
        with cols_fx[i]:
            st.markdown(f'<div class="market-card"><div style="font-size:0.75rem; color:#8892b0;">{TICKER_NAMES.get(t,t)}</div>'
                        f'<div class="metric-value">{last:,.5f}</div>'
                        f'<div style="color:{"#00FFA3" if chg>0 else "#FF4B4B"}; font-size:0.85rem;">{chg:+.2f}%</div></div>', unsafe_allow_html=True)

st.subheader("📈 Markt-Indizes 📈")
SYMBOLS_INDICES = ["^GDAXI", "^STOXX50E", "^NSEI", "XU100.IS"]
cols_ind = st.columns(len(SYMBOLS_INDICES))
for i, t in enumerate(SYMBOLS_INDICES):
    df = get_data(t, period="5d")
    if not df.empty:
        last = float(df['Close'].iloc[-1]); chg = ((last / df['Close'].iloc[-2]) - 1) * 100
        with cols_ind[i]:
            st.markdown(f'<div class="market-card"><div style="font-size:0.75rem; color:#8892b0;">{TICKER_NAMES.get(t,t)}</div>'
                        f'<div class="metric-value">{last:,.2f}</div>'
                        f'<div style="color:{"#00FFA3" if chg>0 else "#FF4B4B"}; font-size:0.85rem;">{chg:+.2f}%</div></div>', unsafe_allow_html=True)

# --- 6. DEEP-DIVE ANALYSE ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    st.subheader("📊 Deep-Dive Chart 📊")
    ca, cb = st.columns(2)
    s_idx = ca.selectbox("Markt:", ["DAX 40 (DE)", "NASDAQ 100 (US)", "BIST 100 (TR)", "Nifty 50 (IN)"])
    STOCKS_DICT = {
        "DAX 40 (DE)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
        "NASDAQ 100 (US)": [k for k in TICKER_NAMES.keys() if not k.endswith(".DE") and not k.endswith(".IS") and not k.endswith(".NS") and not "=" in k and not "^" in k],
        "BIST 100 (TR)": ["THYAO.IS", "ASELS.IS", "KCHOL.IS"],
        "Nifty 50 (IN)": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    }
    s_tkr = cb.selectbox("Wert:", STOCKS_DICT[s_idx], format_func=lambda x: TICKER_NAMES.get(x,x))
    
    d_s = get_data(s_tkr, interval="4h")
    if not d_s.empty:
        cp = float(d_s['Close'].iloc[-1])
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), gridspec_kw={'height_ratios': [3, 1]})
        fig.patch.set_facecolor('#0E1117')
        
        ax1.set_facecolor('#0E1117')
        log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1))
        vol = log_returns.std()
        ends = []
        for _ in range(50):
            p = [cp]
            for _ in range(30): p.append(p[-1] * np.exp(np.random.normal(0, vol)))
            ax1.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.1)
            ends.append(p[-1])
        ax1.axhline(y=cp, color='white', linestyle='--', alpha=0.3); ax1.set_title("Monte Carlo Prognose")

        ax2.set_facecolor('#0E1117')
        rsi_series = calculate_rsi(d_s['Close'])
        ax2.plot(rsi_series.values, color='#1E90FF', linewidth=1.5)
        ax2.axhline(y=70, color='#FF4B4B', linestyle='--', alpha=0.5); ax2.axhline(y=30, color='#00FFA3', linestyle='--', alpha=0.5)
        ax2.set_ylim(0, 100); plt.tight_layout(); st.pyplot(fig)
        
        prob_up = (np.array(ends) > cp).mean() * 100
        st.info(f"Aufwärts-Wahrscheinlichkeit: {prob_up:.1f}%")

with c2:
    st.subheader("🗞️ News Ticker")
    s_obj = yf.Ticker(s_tkr)
    n_list = [n for n in s_obj.news if n.get('title')]
    if n_list:
        # FIX: News HTML mit robuster For-Schleife statt fehlerhafter List-Comprehension
        news_html_body = ""
        for n in n_list:
            title = n.get('title', '')
            link = n.get('link', '#')
            display_title = (title[:75] + '..') if len(title) > 75 else title
            news_html_body += f'<div class="news-item"><a href="{link}" target="_blank" style="color:#1E90FF; text-decoration:none;">{display_title}</a></div>'
        
        st.markdown(f'<div class="news-container"><div class="news-scroll">{news_html_body}{news_html_body}</div></div>', unsafe_allow_html=True)
    else: st.info("Keine News verfügbar.")

# --- 7. SCANNER ---
st.divider()
st.subheader("🎯 High-Prob Scanner (1.000 Sims)")

def run_full_scan():
    all_results = []
    scan_list = []
    for l in STOCKS_DICT.values(): scan_list.extend(l)
    for tkr in scan_list:
        df_sc = get_data(tkr, period="60d")
        if not df_sc.empty:
            cp_sc = float(df_sc['Close'].iloc[-1])
            returns = df_sc['Close'].pct_change().dropna()
            v = returns.std()
            sims = cp_sc * np.exp(np.random.normal(0, v, 1000) * np.sqrt(30))
            all_results.append({
                "Name": TICKER_NAMES.get(tkr, tkr), 
                "Up_Prob": (sims > cp_sc).mean() * 100,
                "Price": cp_sc,
                "SL_Call": cp_sc * (1 - v), "TP_Call": cp_sc * (1 + 1.5 * v),
                "SL_Put": cp_sc * (1 + v), "TP_Put": cp_sc * (1 - 1.5 * v)
            })
    return pd.DataFrame(all_results)

if 'scan_data' not in st.session_state or st.button("🚀 Markt manuell aktualisieren"):
    with st.spinner('Analyse läuft...'):
        st.session_state.scan_data = run_full_scan()

df_res = st.session_state.scan_data
rc, rp = st.columns(2)

with rc:
    st.success("📈 Top 5 Call-Kandidaten")
    calls = df_res.sort_values(by="Up_Prob", ascending=False).head(5).copy()
    calls['SL'] = calls['SL_Call'].map('{:,.2f}'.format)
    calls['Kursziel'] = calls['TP_Call'].map('{:,.2f}'.format)
    st.dataframe(calls[['Name', 'Up_Prob', 'SL', 'Kursziel']], hide_index=True)

with rp:
    st.error("📉 Top 5 Put-Kandidaten")
    puts = df_res.sort_values(by="Up_Prob", ascending=True).head(5).copy()
    puts['Down_Prob'] = 100 - puts['Up_Prob']
    puts['SL'] = puts['SL_Put'].map('{:,.2f}'.format)
    puts['Kursziel'] = puts['TP_Put'].map('{:,.2f}'.format)
    st.dataframe(puts[['Name', 'Down_Prob', 'SL', 'Kursziel']], hide_index=True)
