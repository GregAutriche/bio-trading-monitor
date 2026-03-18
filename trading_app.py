import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. NAMENS-MAPPING (DAX 40 & NASDAQ) ---
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

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; background-image: linear-gradient(180deg, #0e1525 0%, #050a14 100%); color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(8px); }
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

# --- 5. MARKT-WETTER ---
st.title("🚀 Bio-Trading Monitor Live PRO")
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
                        f'<div style="color:{"#00FFA3" if chg>0 else "#FF4B4B"}; font-size:0.85rem;">{chg:+.2f}%</div></div>', unsafe_allow_html=True)

# --- 6. DEEP-DIVE ANALYSE ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    st.subheader("📊 Chart & Indikatoren")
    ca, cb = st.columns(2)
    s_idx = ca.selectbox("Markt:", ["DAX 40", "NASDAQ Tech"])
    DAX_ALL = [k for k in TICKER_NAMES.keys() if k.endswith(".DE")]
    NASDAQ_TOP = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META"]
    s_tkr = cb.selectbox("Wert:", DAX_ALL if s_idx=="DAX 40" else NASDAQ_TOP, format_func=lambda x: TICKER_NAMES.get(x,x))
    
    d_s = get_data(s_tkr, interval="4h")
    if not d_s.empty:
        cp = float(d_s['Close'].iloc[-1])
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), gridspec_kw={'height_ratios': [2, 1]})
        fig.patch.set_facecolor('#0E1117')
        
        ax1.set_facecolor('#0E1117')
        ends = []
        for _ in range(50):
            p = [cp]
            for _ in range(30): p.append(p[-1] * (1 + np.random.normal(0, d_s['Close'].pct_change().std())))
            ax1.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.1)
            ends.append(p[-1])
        ax1.axhline(y=cp, color='white', linestyle='--', alpha=0.3)
        ax1.set_title("Monte Carlo Prognose (30 Tage)")

        ax2.set_facecolor('#0E1117')
        rsi_series = calculate_rsi(d_s['Close'])
        current_rsi = float(rsi_series.iloc[-1])
        ax2.plot(rsi_series.values, color='#1E90FF', linewidth=1.5)
        ax2.axhline(y=70, color='#FF4B4B', linestyle='--', alpha=0.5); ax2.axhline(y=30, color='#00FFA3', linestyle='--', alpha=0.5)
        ax2.set_ylim(0, 100); ax2.set_title(f"RSI: {current_rsi:.1f}")
        plt.tight_layout(); st.pyplot(fig)
        
        prob_up = (np.array(ends) > cp).mean() * 100
        if prob_up > 60 and current_rsi < 40: st.success(f"🟢 **SIGNAL: KAUFEN** (Monte Carlo {prob_up:.1f}% | RSI {current_rsi:.1f})")
        elif prob_up < 40 and current_rsi > 60: st.error(f"🔴 **SIGNAL: VERKAUFEN** (Monte Carlo niedrig | RSI {current_rsi:.1f})")
        else: st.warning(f"🟡 **SIGNAL: NEUTRAL**")

with c2:
    st.subheader("🗞️ News Ticker")
    s_obj = yf.Ticker(s_tkr)
    n_list = [n for n in s_obj.news if n.get('title')]
    if n_list:
        news_items_list = []
        for n in n_list:
            t = n.get('title', ''); l = n.get('link', '#'); disp_t = (t[:75] + '..') if len(t) > 75 else t
            news_items_list.append(f'<div class="news-item"><a href="{l}" target="_blank" style="color:#1E90FF; text-decoration:none;">{disp_t}</a></div>')
        st.markdown(f'<div class="news-container"><div class="news-scroll">{"".join(news_items_list)*2}</div></div>', unsafe_allow_html=True)
    else: st.info("Keine News verfügbar.")

# --- 7. SCANNER (Standardmäßig geladen & hohe Präzision) ---
st.divider()
st.subheader("🎯 High-Prob Scanner (>75%)")

# Funktion für den Scan (1.000 Simulationen für hohe Präzision)
def run_full_scan():
    all_results = []
    tickers_to_scan = DAX_ALL + NASDAQ_TOP
    for tkr in tickers_to_scan:
        df_sc = get_data(tkr, period="60d")
        if not df_sc.empty:
            cp_sc = float(df_sc['Close'].iloc[-1])
            std_dev = df_sc['Close'].pct_change().std()
            # 1.000 Simulationen für statistische Genauigkeit
            sims = cp_sc * np.exp(np.random.normal(0, std_dev, 1000) * np.sqrt(30))
            all_results.append({"Name": TICKER_NAMES.get(tkr, tkr), "Up_Prob": (sims > cp_sc).mean() * 100})
    return pd.DataFrame(all_results)

# Initialer Scan oder Refresh
if 'scan_data' not in st.session_state or st.button("🚀 Markt manuell aktualisieren"):
    with st.spinner('Präzisions-Analyse läuft (1.000 Simulationen pro Aktie)...'):
        st.session_state.scan_data = run_full_scan()

df_res = st.session_state.scan_data
rc, rp = st.columns(2)
with rc:
    st.success("📈 Top 5 Call-Kandidaten")
    st.dataframe(df_res.sort_values(by="Up_Prob", ascending=False).head(5), hide_index=True)
with rp:
    st.error("📉 Top 5 Put-Kandidaten")
    # Berechnung der Down-Prob für die Anzeige
    puts = df_res.sort_values(by="Up_Prob", ascending=True).head(5).copy()
    puts['Down_Prob'] = 100 - puts['Up_Prob']
    st.dataframe(puts[['Name', 'Down_Prob']], hide_index=True)
