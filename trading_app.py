import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING (KLARTEXT) ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50",
    "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    # DAX 40 (VOLLSTÄNDIG)
    "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer",
    "BEI.DE": "Beiersdorf", "BMW.DE": "BMW", "BNR.DE": "Brenntag", "CBK.DE": "Commerzbank", "CON.DE": "Continental",
    "1COV.DE": "Covestro", "DTG.DE": "Daimler Truck", "DBK.DE": "Deutsche Bank", "DB1.DE": "Deutsche Börse",
    "DHL.DE": "DHL Group", "DTE.DE": "Telekom", "EON.DE": "E.ON", "FME.DE": "Fresenius Med.", "FRE.DE": "Fresenius SE",
    "GEA.DE": "GEA Group", "HNR1.DE": "Hannover Rück", "HEI.DE": "Heidelberg Mat.", "HEN3.DE": "Henkel",
    "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "MRK.DE": "Merck", "MTX.DE": "MTU Aero", "MUV2.DE": "Münchener Rück",
    "PAH3.DE": "Porsche SE", "PUM.DE": "Puma", "QIA.DE": "Qiagen", "RHM.DE": "Rheinmetall", "RWE.DE": "RWE",
    "SAP.DE": "SAP", "SIE.DE": "Siemens", "ENR.DE": "Siemens Energy", "SHL.DE": "Siemens Health.", "SY1.DE": "Symrise",
    "VOW3.DE": "Volkswagen", "VNA.DE": "Vonovia", "ZAL.DE": "Zalando",
    # NASDAQ TOP TITEL
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "AMZN": "Amazon", "META": "Meta", "TSLA": "Tesla",
    "GOOGL": "Alphabet", "AVGO": "Broadcom", "COST": "Costco", "NFLX": "Netflix", "AMD": "AMD"
}

TICKER_GROUPS = {
    "DAX 40 (DE)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
    "EuroStoxx 50 (EU)": ["AIR.PA", "MC.PA", "OR.PA", "ASML.AS", "SAN.PA", "BNP.PA", "SAP.DE", "SIE.DE"],
    "NASDAQ 100 (US)": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", "NFLX", "AMD"],
    "BIST 100 (TR)": ["THYAO.IS", "ASELS.IS", "KCHOL.IS"],
    "Nifty 50 (IN)": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; color: white; }
    .bullish { color: #00FFA3 !important; font-weight: bold; }
    .bearish { color: #FF4B4B !important; font-weight: bold; }
    .header-box { padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 25px; border: 1px solid #1E90FF; background: rgba(30,144,255,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN (FEHLER-FIXED) ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="4h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def extract_price(df, idx):
    # Sicherer Extraktions-Fix für den TypeError
    val = df['Close'].iloc[idx]
    return float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)

def run_market_scanner(ticker_list):
    results = []
    for t in ticker_list:
        df = get_data(t, period="5d")
        if not df.empty and len(df) >= 2:
            cp = extract_price(df, -1); prev = extract_price(df, -2)
            trend = ((cp / prev) - 1) * 100
            results.append({"Aktie": TICKER_NAMES.get(t, t), "Kurs": round(cp, 2), "Trend %": round(trend, 2)})
    return pd.DataFrame(results)

# --- 5. AUFBAU ---

# 1. WÄHRUNGEN
st.title("🚀 Bio-Trading Monitor Live PRO")
st.subheader("💱 Währungen")
cf1, cf2, _ = st.columns(3)
for i, t in enumerate(["EURUSD=X", "EURRUB=X"]):
    df_f = get_data(t, period="2d")
    if not df_f.empty:
        l = extract_price(df_f, -1)
        (cf1 if i==0 else cf2).markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.5f}</span></div>', unsafe_allow_html=True)

# 2. INDIZES
st.subheader("📈 Indizes")
cols_i = st.columns(5)
for i, t in enumerate(["^GDAXI", "^STOXX50E", "^NDX", "XU100.IS", "^NSEI"]):
    df_i = get_data(t, period="2d")
    if not df_i.empty:
        l = extract_price(df_i, -1); p = extract_price(df_i, -2); c = ((l/p)-1)*100
        cols_i[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.2f}</span><br><span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

st.divider()

# 3. STEUERUNG
st.subheader("⚙️ Steuerung")
cs1, cs2 = st.columns(2)
sel_market = cs1.selectbox("Markt wählen:", list(TICKER_GROUPS.keys()))
sel_stock = cs2.selectbox("Aktie wählen:", TICKER_GROUPS[sel_market], format_func=lambda x: TICKER_NAMES.get(x, x))

st.divider()

# 4. SCANNER
st.subheader(f"🎯 Scanner: {sel_market}")
scan_results = run_market_scanner(TICKER_GROUPS[sel_market])
if not scan_results.empty:
    col_c, col_p = st.columns(2)
    with col_c:
        st.markdown("<span class='bullish'>🟢 TOP 5 CALLS</span>", unsafe_allow_html=True)
        st.dataframe(scan_results.sort_values(by="Trend %", ascending=False).head(5), use_container_width=True, hide_index=True)
    with col_p:
        st.markdown("<span class='bearish'>🔴 TOP 5 PUTS</span>", unsafe_allow_html=True)
        st.dataframe(scan_results.sort_values(by="Trend %", ascending=True).head(5), use_container_width=True, hide_index=True)

st.divider()

# 5. FOKUS: MONTE CARLO & WETTER
d_s = get_data(sel_stock, period="60d")
if not d_s.empty:
    cp = extract_price(d_s, -1)
    trend_now = ((cp / extract_price(d_s, -2)) - 1) * 100
    
    # --- LOGIK: (C)all / (P)ut ---
    label, icon, color = ("(C)", "☀️", "#00FFA3") if trend_now >= 0 else ("(P)", "⛈️", "#FF4B4B")
    target = cp * 1.05 if trend_now >= 0 else cp * 0.95
    sl_dist = -3.00

    # Fokus-Balken mit Aktionsfarben VOR der Info
    st.markdown(f"""
        <div class="header-box">
            <span style="color:#8892b0;">Fokus:</span> <b style="color:white; font-size:1.1rem; margin-right:15px;">{TICKER_NAMES.get(sel_stock, sel_stock)}</b> 
            <span style="color:#1E90FF;">|</span>
            <span style="color:#8892b0; margin-left:15px;">Kurs:</span> <b style="color:white; font-size:1.1rem; margin-right:15px;">{cp:,.2f}</b> 
            <span style="color:#1E90FF;">|</span>
            <span style="color:{color}; font-weight:bold; font-size:1.2rem; margin-left:15px;">
                {label} Ziel: {target:,.2f} 
                <span style="font-size:0.85rem; color:#8892b0; font-weight:normal;">({sl_dist:+.2f}% SL)</span> {icon}
            </span>
        </div>
    """, unsafe_allow_html=True)

    # Plot
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 4.5))
    fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
    log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)); vol = log_returns.std()
    for _ in range(25):
        p = [cp]; 
        for _ in range(20): p.append(p[-1] * np.exp(np.random.normal(0, vol)))
        ax.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.15)
    st.pyplot(fig)
