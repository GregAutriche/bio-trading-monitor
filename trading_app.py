import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import smtplib
from email.message import EmailMessage
from streamlit_autorefresh import st_autorefresh

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live ULTIMATE", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. ALERT-FUNKTIONEN ---
def play_alert_sound():
    """Spielt ein akustisches Signal ab."""
    audio_html = """
        <audio autoplay>
            <source src="https://www.soundjay.com" type="audio/mpeg">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# --- 3. NAMENS-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX Index", "^STOXX50E": "EuroStoxx 50",
    "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer",
    "BMW.DE": "BMW", "CON.DE": "Continental", "1COV.DE": "Covestro", "DTG.DE": "Daimler Truck",
    "DBK.DE": "Deutsche Bank", "DB1.DE": "Deutsche Börse", "LHA.DE": "Lufthansa", "DTE.DE": "Telekom",
    "EON.DE": "E.ON", "FME.DE": "Fresenius Med.", "FRE.DE": "Fresenius SE", "HLAG.DE": "Hapag-Lloyd",
    "HNR1.DE": "Hannover Rück", "HEI.DE": "Heidelberg Materials", "HFG.DE": "HelloFresh", "HEN3.DE": "Henkel",
    "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "MRK.DE": "Merck KGaA", "MTX.DE": "MTU Aero",
    "MUV2.DE": "Münchener Rück", "PUM.DE": "Puma", "RHM.DE": "Rheinmetall", "RWE.DE": "RWE",
    "SAP.DE": "SAP SE", "SIE.DE": "Siemens AG", "SRT3.DE": "Sartorius", "SHL.DE": "Siemens Health",
    "SY1.DE": "Symrise", "VOW3.DE": "Volkswagen", "VNA.DE": "Vonovia", "ZAL.DE": "Zalando",
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "TSLA": "Tesla", "AMZN": "Amazon", "META": "Meta"
}

# --- 4. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; background-image: linear-gradient(180deg, #0e1525 0%, #050a14 100%); color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(8px); }
    .metric-value { font-size: 1.1rem; font-weight: bold; color: #FFFFFF; font-family: 'Courier New', monospace; }
    .news-container { height: 350px; overflow: hidden; position: relative; border-left: 2px solid #1E90FF; padding-left: 12px; }
    .news-scroll { animation: scroll-up 45s linear infinite; }
    .news-item { margin-bottom: 12px; font-size: 0.85rem; background: rgba(255,255,255,0.05); padding: 8px; border-radius: 8px; }
    @keyframes scroll-up { 0% { transform: translateY(0); } 100% { transform: translateY(-50%); } }
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA FETCHING ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="1d"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

@st.cache_data(ttl=1800)
def get_news_fb(ticker):
    try:
        s = yf.Ticker(ticker); news = [n for n in s.news if n.get('title')]
        if not news:
            m = yf.Ticker("^GDAXI"); news = [n for n in m.news if n.get('title')]
            for n in news: n['is_fb'] = True
        return news[:10]
    except: return []

# --- 6. LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live ULTIMATE")
SYMBOLS_GEN = ["EURUSD=X", "EURRUB=X", "^GDAXI", "^STOXX50E"]
cols = st.columns(len(SYMBOLS_GEN))
for i, t in enumerate(SYMBOLS_GEN):
    df = get_data(t, period="5d")
    if not df.empty:
        last = float(df['Close'].iloc[-1]); chg = ((last / df['Close'].iloc[-2]) - 1) * 100
        fmt = "{:,.5f}" if "=X" in t else "{:,.2f}"
        with cols[i]:
            st.markdown(f'<div class="market-card"><div style="font-size:0.75rem; color:#8892b0;">{TICKER_NAMES.get(t,t)}</div>'
                        f'<div class="metric-value">{fmt.format(last)}</div>'
                        f'<div style="color:{"#00FFA3" if chg>0 else "#FF4B4B"};">{chg:+.2f}%</div></div>', unsafe_allow_html=True)

st.divider()
c1, c2 = st.columns()
with c1:
    st.subheader("📊 Chart-Analyse")
    ca, cb = st.columns(2)
    s_idx = ca.selectbox("Markt:", ["DAX 40", "NASDAQ Tech"])
    DAX_ALL = [k for k in TICKER_NAMES.keys() if k.endswith(".DE")]
    NASDAQ_TOP = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META"]
    s_tkr = cb.selectbox("Wert:", DAX_ALL if s_idx=="DAX 40" else NASDAQ_TOP, format_func=lambda x: TICKER_NAMES.get(x,x))
    
    d_s = get_data(s_tkr, interval="4h")
    if not d_s.empty:
        cp = float(d_s['Close'].iloc[-1])
        plt.style.use('dark_background'); fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
        ends = []
        for _ in range(50):
            p = [cp]
            for _ in range(30): p.append(p[-1] * (1 + np.random.normal(0, d_s['Close'].pct_change().std())))
            ax.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.15)
            ends.append(p[-1])
        st.pyplot(fig)
        st.info(f"Aufwärts-Wahrscheinlichkeit: {(np.array(ends) > cp).mean()*100:.1f}%")

with c2:
    n_list = get_news_fb(s_tkr)
    st.subheader("🗞️ News Ticker")
    if n_list:
        news_html = ""
        for i in n_list:
            link = i.get("link", "#")
            title = i.get("title", "Kein Titel")
            disp_title = (title[:75] + '..') if len(title) > 75 else title
            news_html += f'<div class="news-item"><a href="{link}" target="_blank" style="color:#1E90FF; text-decoration:none;">{disp_title}</a></div>'
        st.markdown(f'<div class="news-container"><div class="news-scroll">{news_html}{news_html}</div></div>', unsafe_allow_html=True)
    else:
        st.info("Keine News verfügbar.")

# --- 7. SCANNER ---
st.divider()
st.subheader("⚡ High-Prob Options Scanner (>75%)")
if st.button("🚀 Markt-Scan & Alerts"):
    results = []; alerts = []
    with st.spinner('Analyse...'):
        for tkr in DAX_ALL + NASDAQ_TOP:
            df_sc = get_data(tkr, period="60d")
            if not df_sc.empty:
                cp = float(df_sc['Close'].iloc[-1])
                sims = cp * np.exp(np.random.normal(0, df_sc['Close'].pct_change().std(), 100) * np.sqrt(30))
                p_up = (sims > cp).mean() * 100
                results.append({"Name": TICKER_NAMES.get(tkr, tkr), "Up": p_up})
                if p_up >= 78: alerts.append(f"🟢 CALL: {TICKER_NAMES.get(tkr,tkr)}")
                elif p_up <= 22: alerts.append(f"🔴 PUT: {TICKER_NAMES.get(tkr,tkr)}")
    
    if alerts:
        play_alert_sound()
        for a in alerts: st.toast(a, icon='⚡')
    
    df_res = pd.DataFrame(results)
    rc, rp = st.columns(2)
    with rc:
        st.success("📈 Call Kandidaten")
        st.dataframe(df_res[df_res['Up']>=70].sort_values(by="Up", ascending=False), hide_index=True)
    with rp:
        st.error("📉 Put Kandidaten")
        st.dataframe(df_res[df_res['Up']<=30].sort_values(by="Up", ascending=True), hide_index=True)
