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
    "AD.AS": "Ahold Delhaize", "ADS.DE": "Adidas", "AIR.PA": "Airbus", "ALV.DE": "Allianz", "ASML.AS": "ASML",
    "BAS.DE": "BASF", "BAYN.DE": "Bayer", "BMW.DE": "BMW", "DHL.DE": "DHL Group", "DTE.DE": "Telekom",
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "AMD": "AMD", "NFLX": "Netflix", "RHM.DE": "Rheinmetall"
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
    .alert-box { padding: 15px; border-radius: 8px; margin-bottom: 10px; font-weight: bold; text-align: center; }
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
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        return pd.DataFrame()

def extract_price(df, idx):
    try:
        if df.empty: return 0.0
        val = df['Close'].iloc[idx]
        return float(val.iloc) if isinstance(val, (pd.Series, np.ndarray)) else float(val)
    except: return 0.0

# --- 5. AUFBAU ---
st.title("🚀 Bio-Trading Monitor Live PRO")

cs1, cs2 = st.columns(2)
sel_market = cs1.selectbox("Markt wählen:", list(TICKER_GROUPS.keys()))
sorted_stocks = sorted(TICKER_GROUPS[sel_market], key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = cs2.selectbox("Aktie wählen:", sorted_stocks, format_func=lambda x: TICKER_NAMES.get(x, x))

st.divider()

d_s = get_data(sel_stock)

if not d_s.empty and 'Volume' in d_s.columns:
    
    # DATEN-BERECHNUNG
    cur_vol = float(d_s['Volume'].iloc[-1])
    vol_20d = d_s['Volume'].tail(120)
    avg_20d = vol_20d.mean()
    v_trend_20d = ((cur_vol / avg_20d) - 1) * 100 if avg_20d > 0 else 0
    
    # --- NEU: VOLUMEN-ALERTS (BENACHRICHTIGUNG) ---
    if v_trend_20d > 50:
        st.markdown(f'<div class="alert-box" style="background: rgba(0, 255, 163, 0.2); border: 1px solid #00FFA3; color: #00FFA3;">🔥 VOLUMEN-ALARM: Starker Kaufdruck! (+{v_trend_20d:.1f}% über Schnitt)</div>', unsafe_allow_html=True)
    elif v_trend_20d < -50:
        st.markdown(f'<div class="alert-box" style="background: rgba(255, 75, 75, 0.2); border: 1px solid #FF4B4B; color: #FF4B4B;">⚠️ LIQUIDITÄTS-ALARM: Handelsvolumen extrem niedrig! ({v_trend_20d:.1f}%)</div>', unsafe_allow_html=True)

    # HANDELS-LOGIK
    log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)).dropna()
    vol_std = log_returns.std()
    ann_vol = vol_std * np.sqrt(252 * 6) * 100
    cp = extract_price(d_s, -1)

    np.random.seed(int(pd.Timestamp.now().timestamp() // 86400) + hash(sel_stock) % 1000)
    sim_results = [cp * np.exp(np.random.normal(0, vol_std * np.sqrt(15))) for _ in range(100)]
    is_long = bool(np.median(sim_results) >= cp)
    t_up, t_down = np.percentile(sim_results, 95), np.percentile(sim_results, 5)
    sig_t, sig_i, sig_c = (("LONG EINSTIEG", "🟢", "#00FFA3") if is_long and ann_vol < 45 else ("SHORT CHANCE", "🔴", "#FF4B4B") if not is_long and ann_vol < 45 else ("ABWARTEN", "⚪", "#8892b0"))

    # HEADER & SETUP
    st.markdown(f'<div class="header-box" style="border-color:{sig_c};"><b style="font-size:1.3rem; color:white;">{TICKER_NAMES.get(sel_stock, sel_stock)}</b> <span style="color:#1E90FF; margin: 0 15px;">|</span> Vola: <b>{ann_vol:.1f}%</b> <span style="color:#1E90FF; margin: 0 15px;">|</span> Trend 20d: <b style="color:{"#00FFA3" if v_trend_20d > 0 else "#FF4B4B"};">{v_trend_20d:+.1f}%</b></div>', unsafe_allow_html=True)
    
    dir_l, dir_col = ("[ CALL ]", "#00FFA3") if is_long else ("[ PUT ]", "#FF4B4B")
    st.markdown(f"### 📝 Handels-Setup: <span style='color:{dir_col};'>{dir_l}</span> <span style='float:right; font-size:1rem; color:{sig_c};'>{sig_i} {sig_t}</span>", unsafe_allow_html=True)

    target_p = t_up if is_long else t_down
    stop_l = cp * 0.97 if is_long else cp * 1.03
    crv = abs(target_p - cp) / abs(cp - stop_l) if abs(cp - stop_l) > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("EINSTIEG", f"{cp:,.2f}")
    c2.metric("ZIEL (TP)", f"{target_p:,.2f}", f"{(target_p/cp-1)*100:+.2f}%")
    c3.metric("STOP LOSS", f"{stop_l:,.2f}", f"{(stop_l/cp-1)*100:+.2f}%")
    c4.metric("VOLUMEN", f"{cur_vol:,.0f}", f"{v_trend_20d:+.1f}%")
    
    crv_col = "#00FFA3" if crv >= 2 else "#FFD700" if crv >= 1.5 else "#FF4B4B"
    c5.markdown(f'<div style="text-align:center; background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; border: 1px solid {crv_col};"><small style="color:#8892b0;">CRV</small><br><span style="font-size:1.5rem; font-weight:bold; color:{crv_col};">{crv:.2f}</span></div>', unsafe_allow_html=True)

    # --- VOLUMENSINFO BEREICH ---
    st.divider()
    st.subheader("📊 Volumensinfo (Letzte 20 Handelstage)")
    vcol1, vcol2 = st.columns([1, 2])
    
    with vcol1:
        st.metric("Durchschnitt (20d)", f"{avg_20d:,.0f}")
        st.metric("Abweichung", f"{v_trend_20d:+.1f}%")
        st.info("💡 Ein hohes Volumen bestätigt oft den Trendbruch.")

    with vcol2:
        st.bar_chart(d_s['Volume'].tail(40))

else:
    st.warning("Keine Volumendaten verfügbar.")

# FOOTER
st.info(f"🕒 Stand: {pd.Timestamp.now().strftime('%d.%m.%Y | %H:%M:%S')} | 📊 Analyse: 4h-Intervall")
