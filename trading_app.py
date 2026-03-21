import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING (KLARTEXT-NAMEN) ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50",
    "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    "AD.AS": "Ahold Delhaize", "ADS.DE": "Adidas", "AIR.PA": "Airbus", "ALV.DE": "Allianz", "ASML.AS": "ASML",
    "BAS.DE": "BASF", "BAYN.DE": "Bayer", "BMW.DE": "BMW", "DHL.DE": "DHL Group", "DTE.DE": "Telekom",
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "AMD": "AMD", "NFLX": "Netflix"
}

TICKER_GROUPS = {
    "EuroStoxx 50 (EU)": ["AD.AS", "ADS.DE", "AIR.PA", "ALV.DE", "ASML.AS", "BAS.DE", "BAYN.DE", "BMW.DE", "DHL.DE", "DTE.DE"],
    "DAX 40 (DE)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
    "NASDAQ 100 (US)": ["AAPL", "MSFT", "NVDA", "NFLX", "AMD"]
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .header-box { padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 25px; border: 1px solid #1E90FF; background: rgba(30,144,255,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="4h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.get_level_values(0)
        return d
    except:
        return pd.DataFrame()

def extract_price(df, idx):
    try:
        if df.empty:
            return 0.0
        val = df['Close'].iloc[idx]
        return float(val) if not isinstance(val, (pd.Series, np.ndarray)) else float(val.iloc)
    except:
        return 0.0

# --- 5. AUFBAU ---
st.title("🚀 Bio-Trading Monitor Live PRO")

cs1, cs2 = st.columns(2)
sel_market = cs1.selectbox("Markt wählen:", list(TICKER_GROUPS.keys()))
sorted_stocks = sorted(TICKER_GROUPS[sel_market], key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = cs2.selectbox("Aktie wählen:", sorted_stocks, format_func=lambda x: TICKER_NAMES.get(x, x))

st.divider()

# --- DER FOKUS-BLOCK ---
d_s = get_data(sel_stock, period="60d")

if not d_s.empty:

    # A. VOLUMEN-LOGIK
    avg_vol = d_s['Volume'].tail(10).mean()
    cur_vol = d_s['Volume'].iloc[-1]
    v_diff = ((cur_vol / avg_vol) - 1) * 100 if avg_vol > 0 else 0
    v_icon, v_col = ("🔥", "#00FFA3") if v_diff > 15 else ("💤", "#FF4B4B") if v_diff < -15 else ("📊", "#8892b0")
    v_status = "Bestätigt" if v_diff > 15 else "Schwach" if v_diff < -15 else "Normal"

    # B. PROGNOSE-DATEN
    log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)).dropna()
    vol = log_returns.std()
    ann_vol = vol * np.sqrt(252) * 100
    cp = extract_price(d_s, -1)

    # Simulation
    np.random.seed(int(pd.Timestamp.now().timestamp() // 86400) + hash(sel_stock) % 1000)
    sim_results = [cp * np.exp(np.random.normal(0, vol * np.sqrt(15))) for _ in range(100)]
    is_long = bool(np.median(sim_results) >= cp)
    t_up, t_down = np.percentile(sim_results, 95), np.percentile(sim_results, 5)
    sig_t, sig_i, sig_c = (
        ("LONG EINSTIEG", "🟢", "#00FFA3") if is_long and ann_vol < 35 else
        ("SHORT CHANCE", "🔴", "#FF4B4B") if not is_long and ann_vol < 35 else
        ("ABWARTEN", "⚪", "#8892b0")
    )

    # 1. HEADER
    st.markdown(f"""
        <div class="header-box" style="border-color:{sig_c};">
            <b style="font-size:1.3rem; color:white;">{TICKER_NAMES.get(sel_stock, sel_stock)}</b> 
            <span style="color:#1E90FF; margin: 0 15px;">|</span>
            Vola: <b>{ann_vol:.1f}%</b> 
            <span style="color:#1E90FF; margin: 0 15px;">|</span>
            Volumen: <b style="color:{v_col};">{v_icon} {v_diff:+.1f}%</b>
        </div>
    """, unsafe_allow_html=True)

    # 2. HANDELS-SETUP
    dir_l, dir_col = ("[ CALL ]", "#00FFA3") if is_long else ("[ PUT ]", "#FF4B4B")
    st.markdown(
        f"### 📝 Handels-Setup: <span style='color:{dir_col};'>{dir_l}</span> "
        f"<span style='float:right; font-size:1rem; color:{sig_c};'>{sig_i} {sig_t}</span>",
        unsafe_allow_html=True
    )

    target_p = t_up if is_long else t_down
    stop_l = cp * 0.97 if is_long else cp * 1.03
    risk = abs(cp - stop_l)
    reward = abs(target_p - cp)
    crv = reward / risk if risk > 0 else 0

    # 5 SPALTEN
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("EINSTIEG", f"{cp:,.2f}")
    c2.metric("ZIEL (TP)", f"{target_p:,.2f}", f"{(target_p/cp-1)*100:+.2f}%")
    c3.metric("STOP LOSS", f"{stop_l:,.2f}", f"{(stop_l/cp-1)*100:+.2f}%")

    # Volumen-Spalte
    c4.metric("VOLUMEN", f"{v_icon} {v_diff:+.1f}%", v_status)

    # CRV
    crv_col = "#00FFA3" if crv >= 2 else "#FFD700" if crv >= 1.5 else "#FF4B4B"
    c5.markdown(f"""
        <div style="text-align:center; background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; border: 1px solid {crv_col};">
            <small style="color:#8892b0;">CRV</small><br>
            <span style="font-size:1.5rem; font-weight:bold; color:{crv_col};">{crv:.2f}</span>
        </div>
    """, unsafe_allow_html=True)

    # --- KOMPAKTE VOLUMEN-ZUSAMMENFASSUNG ---
    vol_last_5 = d_s['Volume'].tail(5).mean()
    vol_last_10 = d_s['Volume'].tail(10).mean()
    vol_ratio = (vol_last_5 / vol_last_10 - 1) * 100 if vol_last_10 > 0 else 0
    vol_trend_icon = "📈" if vol_ratio > 5 else "📉" if vol_ratio < -5 else "➡️"

    st.markdown(f"""
    **📊 Volumen-Trend (5 vs. 10 Perioden):**  
    <span style='font-size:1.2rem; color:#1E90FF;'>{vol_trend_icon} {vol_ratio:+.1f}%</span>
    """, unsafe_allow_html=True)

# FOOTER
st.info(f"🕒 Stand: {pd.Timestamp.now().strftime('%d.%m.%Y | %H:%M:%S')} | 📊 Analyse: 4h-Intervall")
