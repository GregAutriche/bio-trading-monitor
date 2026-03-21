import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING (VOLLSTÄNDIG) ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50",
    "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    # EURO STOXX 50 (Auswahl der wichtigsten)
    "ASML.AS": "ASML", "MC.PA": "LVMH", "SAP.DE": "SAP", "OR.PA": "L'Oréal", "ADS.DE": "Adidas", 
    "AIR.PA": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer", "BMW.DE": "BMW",
    "DHL.DE": "DHL Group", "DTE.DE": "Telekom", "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz",
    "MRK.DE": "Merck", "MUV2.DE": "Münchener Rück", "RHM.DE": "Rheinmetall", "SIE.DE": "Siemens",
    "VOW3.DE": "Volkswagen", "VNA.DE": "Vonovia",
    # NASDAQ
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "AMZN": "Amazon", "META": "Meta", "TSLA": "Tesla",
    "GOOGL": "Alphabet", "AVGO": "Broadcom", "COST": "Costco", "NFLX": "Netflix", "AMD": "AMD"
}

TICKER_GROUPS = {
    "EuroStoxx 50 (EU)": ["ASML.AS", "MC.PA", "SAP.DE", "OR.PA", "ADS.DE", "AIR.PA", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "DHL.DE", "DTE.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MUV2.DE", "RHM.DE", "SIE.DE", "VOW3.DE", "VNA.DE"],
    "DAX 40 (DE)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
    "NASDAQ 100 (US)": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", "NFLX", "AMD"]
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; color: white; }
    .sig-call { color: #00FFA3; font-weight: bold; font-size: 0.85rem; }
    .sig-put { color: #FF4B4B; font-weight: bold; font-size: 0.85rem; }
    .sig-neutral { color: #8892b0; font-weight: bold; font-size: 0.85rem; }
    .header-box { padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 25px; border: 1px solid #1E90FF; background: rgba(30,144,255,0.05); }
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
        if df.empty: return 0.0
        val = df['Close'].iloc[idx]
        return float(val) if not isinstance(val, (pd.Series, np.ndarray)) else float(val.iloc)
    except: return 0.0

def run_market_scanner(ticker_list):
    results = []
    data = yf.download(ticker_list, period="60d", interval="4h", progress=False)
    if isinstance(data.columns, pd.MultiIndex): close_p = data['Close']
    else: close_p = data[['Close']]
    # Seed für stabile Simulation am Wochenende
    seed_val = int(pd.Timestamp.now().timestamp() // 86400)
    for t in ticker_list:
        try:
            series = close_p[t].dropna()
            if len(series) > 10:
                cp = series.iloc[-1]; log_r = np.log(series / series.shift(1)).dropna()
                vol = log_r.std(); ann_vol = vol * np.sqrt(252) * 100
                np.random.seed(seed_val + hash(t) % 1000)
                sim_move = np.mean([np.exp(np.random.normal(0, vol)) for _ in range(50)])
                trend_sim = (sim_move - 1) * 100
                status = "🟢" if trend_sim > 0.15 and ann_vol < 35 else "🔴" if trend_sim < -0.15 and ann_vol < 35 else "⚪"
                results.append({"Aktie": TICKER_NAMES.get(t, t), "Kurs": round(cp, 2), "Prognose %": round(trend_sim, 2), "Status": status})
        except: continue
    return pd.DataFrame(results)

def draw_info_card(col, t, is_currency=False):
    df = get_data(t, period="5d")
    if not df.empty:
        l = extract_price(df, -1); p = extract_price(df, -2); diff = ((l/p)-1)*100
        prec = 4 if is_currency else 2
        
        # Die Logik für Farben, Icons und Texte
        if diff > 0.15: 
            sig, icon, css, icon_clr = "CALL (STARK)", "☀️", "sig-call", "#00FFA3"
        elif diff < -0.15: 
            sig, icon, css, icon_clr = "PUT (BEARISH)", "⛈️", "sig-put", "#FF4B4B"
        else: 
            sig, icon, css, icon_clr = "NEUTRAL", "⛅", "sig-neutral", "#8892b0"
            
        col.markdown(f"""
            <div class="market-card">
                <small style="color:#8892b0;">{TICKER_NAMES.get(t,t)}</small>
                <span style="float:right; font-size:1.2rem; color:{icon_clr};">{icon}</span><br>
                <span class="metric-value">{l:,.{prec}f}</span><br>
                <span class="{css}">{sig} ({diff:+.2f}%)</span>
            </div>
        """, unsafe_allow_html=True)

# --- 5. AUFBAU ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# A. WÄHRUNGEN
st.subheader("💱 Fokus/ Währungen")
cw1, cw2, _ = st.columns(3)
draw_info_card(cw1, "EURUSD=X", True); draw_info_card(cw2, "EURRUB=X", True)

# B. INDIZES
st.subheader("📈 Fokus/ Indizes")
c_r1 = st.columns(2); draw_info_card(c_r1[0], "^GDAXI"); draw_info_card(c_r1[1], "^NDX")
c_r2 = st.columns(3); draw_info_card(c_r2[0], "^STOXX50E"); draw_info_card(c_r2[1], "XU100.IS"); draw_info_card(c_r2[2], "^NSEI")

st.divider()

# C. STEUERUNG & SCANNER
cs1, cs2 = st.columns(2)
sel_market = cs1.selectbox("Markt wählen:", list(TICKER_GROUPS.keys()))
sorted_stocks = sorted(TICKER_GROUPS[sel_market], key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = cs2.selectbox("Aktie wählen:", sorted_stocks, format_func=lambda x: TICKER_NAMES.get(x, x))

# D. SCANNER
st.subheader(f"🎯 Prognose-Scanner: {sel_market}")
scan_res = run_market_scanner(TICKER_GROUPS[sel_market])
if not scan_res.empty:
    col_c, col_p = st.columns(2)
    with col_c:
        st.markdown("<span style='color:#00FFA3; font-weight:bold;'>🟢 TOP 5 CALLS</span>", unsafe_allow_html=True)
        st.dataframe(scan_res[scan_res['Prognose %'] > 0].sort_values(by="Prognose %", ascending=False).head(5), use_container_width=True, hide_index=True)
    with col_p:
        st.markdown("<span style='color:#FF4B4B; font-weight:bold;'>🔴 TOP 5 PUTS</span>", unsafe_allow_html=True)
        st.dataframe(scan_res[scan_res['Prognose %'] < 0].sort_values(by="Prognose %", ascending=True).head(5), use_container_width=True, hide_index=True)

st.divider()

# E. ANALYSE & SETUP
d_s = get_data(sel_stock, period="60d")
if not d_s.empty:
    log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)).dropna()
    vol = log_returns.std(); ann_vol = vol * np.sqrt(252) * 100; cp = extract_price(d_s, -1)
    # Stabile Simulation (Seed)
    np.random.seed(int(pd.Timestamp.now().timestamp() // 86400) + hash(sel_stock) % 1000)
    sim_results = [cp * np.exp(np.random.normal(0, vol * np.sqrt(15))) for _ in range(100)]
    is_long = bool(np.median(sim_results) >= cp)
    t_up, t_down = np.percentile(sim_results, 95), np.percentile(sim_results, 5)
    sig_t, sig_i, sig_c = ("LONG EINSTIEG", "🟢", "#00FFA3") if is_long and ann_vol < 35 else ("SHORT CHANCE", "🔴", "#FF4B4B") if not is_long and ann_vol < 35 else ("ABWARTEN", "⚪", "#8892b0")
    
    st.markdown(f'<div class="header-box" style="border-color:{sig_c};"><b>{TICKER_NAMES.get(sel_stock, sel_stock)}</b> | Vola: <b>{ann_vol:.1f}%</b></div>', unsafe_allow_html=True)
    
    dir_label, dir_col = ("[ CALL ]", "#00FFA3") if is_long else ("[ PUT ]", "#FF4B4B")
    st.markdown(f"### 📝 Handels-Setup: <span style='color:{dir_col};'>{dir_label}</span> <span style='float:right; font-size:1rem; color:{sig_c};'>{sig_i} {sig_t}</span>", unsafe_allow_html=True)
    
    target_p = t_up if is_long else t_down; stop_l = cp * 0.97 if is_long else cp * 1.03
    risk = abs(cp - stop_l); reward = abs(target_p - cp); crv = reward / risk if risk > 0 else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EINSTIEG", f"{cp:,.2f}")
    c2.metric("ZIEL (TP)", f"{target_p:,.2f}", f"{(target_p/cp-1)*100:+.2f}%", delta_color="normal" if is_long else "inverse")
    c3.metric("STOP LOSS", f"{stop_l:,.2f}", f"{(stop_l/cp-1)*100:+.2f}%", delta_color="inverse" if is_long else "normal")
    crv_col = "#00FFA3" if crv >= 2 else "#FFD700" if crv >= 1.5 else "#FF4B4B"
    c4.markdown(f'<div style="text-align:center; background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; border: 1px solid {crv_col};"><small>CRV</small><br><span style="font-size:1.5rem; font-weight:bold; color:{crv_col};">{crv:.2f}</span></div>', unsafe_allow_html=True)

# FOOTER
st.info(f"🕒 Stand: {pd.Timestamp.now().strftime('%d.%m.%Y | %H:%M:%S')} | 📊 Analyse: 4h-Intervall")
