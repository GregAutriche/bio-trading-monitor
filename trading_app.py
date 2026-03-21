import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50",
    "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer",
    "BEI.DE": "Beiersdorf", "BMW.DE": "BMW", "BNR.DE": "Brenntag", "CBK.DE": "Commerzbank", "CON.DE": "Continental",
    "1COV.DE": "Covestro", "DTG.DE": "Daimler Truck", "DBK.DE": "Deutsche Bank", "DB1.DE": "Deutsche Börse",
    "DHL.DE": "DHL Group", "DTE.DE": "Telekom", "EON.DE": "E.ON", "FME.DE": "Fresenius Med.", "FRE.DE": "Fresenius SE",
    "GEA.DE": "GEA Group", "HNR1.DE": "Hannover Rück", "HEI.DE": "Heidelberg Mat.", "HEN3.DE": "Henkel",
    "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "MRK.DE": "Merck", "MTX.DE": "MTU Aero", "MUV2.DE": "Münchener Rück",
    "PAH3.DE": "Porsche SE", "PUM.DE": "Puma", "QIA.DE": "Qiagen", "RHM.DE": "Rheinmetall", "RWE.DE": "RWE",
    "SAP.DE": "SAP", "SIE.DE": "Siemens", "ENR.DE": "Siemens Energy", "SHL.DE": "Siemens Health.", "SY1.DE": "Symrise",
    "VOW3.DE": "Volkswagen", "VNA.DE": "Vonovia", "ZAL.DE": "Zalando",
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "AMZN": "Amazon", "META": "Meta", "TSLA": "Tesla",
    "GOOGL": "Alphabet", "AVGO": "Broadcom", "COST": "Costco", "NFLX": "Netflix", "AMD": "AMD"
}

TICKER_GROUPS = {
    "DAX 40 (DE)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
    "NASDAQ 100 (US)": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", "NFLX", "AMD"]
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; color: white; }
    .bullish { color: #00FFA3 !important; font-weight: bold; }
    .bearish { color: #FF4B4B !important; font-weight: bold; }
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

def extract_price(df, idx):
    try:
        val = df['Close'].iloc[idx]
        return float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)
    except: return 0.0

# --- 5. AUFBAU ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 1. WÄHRUNGEN MIT SIGNAL
st.subheader("💱 Fokus/ Währungen 💱")
cf1, cf2, _ = st.columns(3)
for i, t in enumerate(["EURUSD=X", "EURRUB=X"]):
    df_f = get_data(t, period="5d")
    if not df_f.empty:
        l = extract_price(df_f, -1); p = extract_price(df_f, -2)
        diff = ((l/p)-1)*100
        sig = "STARK" if diff > 0.1 else "SCHWACH" if diff < -0.1 else "NEUTRAL"
        sig_clr = "#00FFA3" if diff > 0.1 else "#FF4B4B" if diff < -0.1 else "#8892b0"
        (cf1 if i==0 else cf2).markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.4f}</span> <span style="color:{sig_clr}; font-size:0.8rem; float:right;">{sig} ({diff:+.2f}%)</span></div>', unsafe_allow_html=True)

st.divider()

# 2. STEUERUNG
cs1, cs2 = st.columns(2)
sel_market = cs1.selectbox("Markt wählen:", list(TICKER_GROUPS.keys()))
sel_stock = cs2.selectbox("Aktie wählen:", TICKER_GROUPS[sel_market], format_func=lambda x: TICKER_NAMES.get(x, x))

# 3. ANALYSE & MONTE CARLO
d_s = get_data(sel_stock, period="60d")
if not d_s.empty:
    log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)).dropna()
    vol = log_returns.std(); ann_vol = vol * np.sqrt(252) * 100
    cp = extract_price(d_s, -1); trend = ((cp / extract_price(d_s, -2)) - 1) * 100

    # Signal-Logik
    if trend > 0.5 and ann_vol < 25: sig_t, sig_i, sig_c = "LONG EINSTIEG", "🟢", "#00FFA3"
    elif trend < -0.5: sig_t, sig_i, sig_c = "SHORT CHANCE", "🔴", "#FF4B4B"
    else: sig_t, sig_i, sig_c = "ABWARTEN", "⚪", "#8892b0"

    # Monte Carlo (15 Tage)
    n_sims = 40; sim_results = []
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
    for _ in range(n_sims):
        prices = [cp]
        for _ in range(15): prices.append(prices[-1] * np.exp(np.random.normal(0, vol)))
        sim_results.append(prices[-1]); ax.plot(prices, color=sig_c, alpha=0.1)
    
    t_up, t_down = np.percentile(sim_results, 95), np.percentile(sim_results, 5)
    st.pyplot(fig)

    # --- 6. ORDER-BOARD (CALL/PUT) ---
    is_long = trend >= 0
    dir_label = "[ CALL / LONG ]" if is_long else "[ PUT / SHORT ]"
    dir_col = "#00FFA3" if is_long else "#FF4B4B"

    st.markdown(f"### 📝 Handels-Setup: <span style='color:{dir_col};'>{dir_label}</span>", unsafe_allow_html=True)
    
    entry = cp
    target_price = t_up if is_long else t_down
    stop_loss = cp * 0.97 if is_long else cp * 1.03
    
    risk = abs(entry - stop_loss); reward = abs(target_price - entry)
    crv = reward / risk if risk > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EINSTIEG", f"{entry:,.2f}")
    c2.metric("ZIEL (TP)", f"{target_price:,.2f}", f"{(target_price/entry-1)*100:+.2f}%", delta_color="normal" if is_long else "inverse")
    c3.metric("STOP LOSS", f"{stop_loss:,.2f}", f"{(stop_loss/entry-1)*100:+.2f}%", delta_color="inverse" if is_long else "normal")
    
    crv_c = "#00FFA3" if crv >= 2 else "#FFD700" if crv >= 1.5 else "#FF4B4B"
    c4.markdown(f'<div style="text-align:center; background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; border: 1px solid {crv_c};"><small>CRV</small><br><span style="font-size:1.5rem; font-weight:bold; color:{crv_c};">{crv:.2f}</span></div>', unsafe_allow_html=True)

st.info(f"Update: {pd.Timestamp.now().strftime('%H:%M:%S')}")
