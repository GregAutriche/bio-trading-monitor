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
        return float(val) if not isinstance(val, (pd.Series, np.ndarray)) else float(val.iloc[0])
    except: return 0.0

def run_market_scanner(ticker_list):
    results = []
    data = yf.download(ticker_list, period="60d", interval="4h", progress=False)
    if isinstance(data.columns, pd.MultiIndex): close_p = data['Close']
    else: close_p = data[['Close']]
    for t in ticker_list:
        try:
            series = close_p[t].dropna()
            if len(series) > 10:
                cp = series.iloc[-1]
                log_r = np.log(series / series.shift(1)).dropna()
                vol = log_r.std()
                sim_move = np.mean([np.exp(np.random.normal(0, vol)) for _ in range(50)])
                trend_sim = (sim_move - 1) * 100
                results.append({"Aktie": TICKER_NAMES.get(t, t), "Kurs": round(cp, 2), "Prognose %": round(trend_sim, 2)})
        except: continue
    return pd.DataFrame(results)

# --- 5. AUFBAU ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 1. WÄHRUNGEN MIT WETTER & AKTION
st.subheader("💱 Fokus/ Währungen")
cw1, cw2, _ = st.columns(3)
for i, t in enumerate(["EURUSD=X", "EURRUB=X"]):
    df_f = get_data(t, period="5d")
    if not df_f.empty:
        l = extract_price(df_f, -1); p = extract_price(df_f, -2); diff = ((l/p)-1)*100
        
        # Wetter & Aktions-Logik
        if diff > 0.15: sig, icon, clr = "CALL (STARK)", "☀️", "#00FFA3"
        elif diff < -0.15: sig, icon, clr = "PUT (SCHWACH)", "⛈️", "#FF4B4B"
        else: sig, icon, clr = "NEUTRAL", "⛅", "#8892b0"
        
        (cw1 if i==0 else cw2).markdown(f"""
            <div class="market-card">
                <small>{TICKER_NAMES.get(t,t)}</small>
                <span style="float:right; font-size:1.2rem;">{icon}</span><br>
                <span class="metric-value">{l:,.4f}</span><br>
                <span style="color:{clr}; font-size:0.85rem; font-weight:bold;">{sig} ({diff:+.2f}%)</span>
            </div>
        """, unsafe_allow_html=True)


# 2. INDIZES (GELÖST: WIEDER DA)
st.subheader("📈 Fokus/ Indizes")
cols_row1 = st.columns([1, 1, 2]) # 2 Spalten + Platzhalter für Optik
for i, t in enumerate(["^GDAXI", "^NDX"]):
    df_i = get_data(t, period="2d")
    if not df_i.empty:
        l = extract_price(df_i, -1); p = extract_price(df_i, -2); c = ((l/p)-1)*100
        cols_row1[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.2f}</span><br><span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

# Zweite Zeile: Die restlichen Indizes
cols_row2 = st.columns(3)
for i, t in enumerate(["^STOXX50E", "XU100.IS", "^NSEI"]):
    df_i = get_data(t, period="2d")
    if not df_i.empty:
        l = extract_price(df_i, -1); p = extract_price(df_i, -2); c = ((l/p)-1)*100
        cols_row2[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.2f}</span><br><span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)
st.divider()

# 3. SCANNER (SYNCHRONISIERT)
cs1, cs2 = st.columns(2)
sel_market = cs1.selectbox("Markt wählen:", list(TICKER_GROUPS.keys()))
sel_stock = cs2.selectbox("Aktie wählen:", TICKER_GROUPS[sel_market], format_func=lambda x: TICKER_NAMES.get(x, x))

st.subheader(f"🎯 Prognose-Scanner: {sel_market}")
scan_res = run_market_scanner(TICKER_GROUPS[sel_market])
if not scan_res.empty:
    col_c, col_p = st.columns(2)
    with col_c:
        st.markdown("<span class='bullish'>🟢 TOP 5 CALL-PROGNOSEN</span>", unsafe_allow_html=True)
        st.dataframe(scan_res[scan_res['Prognose %'] > 0].sort_values(by="Prognose %", ascending=False).head(5), use_container_width=True, hide_index=True)
    with col_p:
        st.markdown("<span class='bearish'>🔴 TOP 5 PUT-PROGNOSEN</span>", unsafe_allow_html=True)
        st.dataframe(scan_res[scan_res['Prognose %'] < 0].sort_values(by="Prognose %", ascending=True).head(5), use_container_width=True, hide_index=True)

st.divider()

# 4. FOKUS ANALYSE
d_s = get_data(sel_stock, period="60d")
if not d_s.empty:
    log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)).dropna()
    vol = log_returns.std(); ann_vol = vol * np.sqrt(252) * 100
    cp = extract_price(d_s, -1)

    # Simulation
    n_sims = 40; sim_results = []
    for _ in range(n_sims):
        prices = [cp]
        for _ in range(15): prices.append(prices[-1] * np.exp(np.random.normal(0, vol)))
        sim_results.append(prices[-1])
    
    # Zentrale Logik (Synchronisiert)
    sim_median = float(np.median(sim_results))
    is_long = bool(sim_median >= cp)
    t_up, t_down = np.percentile(sim_results, 95), np.percentile(sim_results, 5)
    sig_t, sig_i, sig_c = ("LONG EINSTIEG", "🟢", "#00FFA3") if is_long and ann_vol < 35 else \
                          ("SHORT CHANCE", "🔴", "#FF4B4B") if not is_long and ann_vol < 35 else \
                          ("ABWARTEN", "⚪", "#8892b0")

    st.markdown(f'<div class="header-box" style="border-color:{sig_c};"><b>{TICKER_NAMES.get(sel_stock, sel_stock)}</b> | Vola: <b>{ann_vol:.1f}%</b></div>', unsafe_allow_html=True)

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
    for res in sim_results:
        ax.plot([cp, res], color=sig_c, alpha=0.1)
    ax.axhline(t_up, color='#00FFA3', ls='--', alpha=0.3); ax.axhline(t_down, color='#FF4B4B', ls='--', alpha=0.3)
    st.pyplot(fig)

    # 5. HANDELS-SETUP
    dir_label = "[ CALL ]" if is_long else "[ PUT ]"
    dir_col = "#00FFA3" if is_long else "#FF4B4B"
    st.markdown(f"### 📝 Handels-Setup: <span style='color:{dir_col};'>{dir_label}</span> <span style='float:right; font-size:1rem; color:{sig_c};'>{sig_i} {sig_t}</span>", unsafe_allow_html=True)
    
    entry = cp; target_p = t_up if is_long else t_down; stop_l = cp * 0.97 if is_long else cp * 1.03
    risk = abs(entry - stop_l); reward = abs(target_p - entry); crv = reward / risk if risk > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EINSTIEG", f"{entry:,.2f}")
    c2.metric("ZIEL (TP)", f"{target_p:,.2f}", f"{(target_p/entry-1)*100:+.2f}%", delta_color="normal" if is_long else "inverse")
    c3.metric("STOP LOSS", f"{stop_l:,.2f}", f"{(stop_l/entry-1)*100:+.2f}%", delta_color="inverse" if is_long else "normal")
    crv_c = "#00FFA3" if crv >= 2 else "#FFD700" if crv >= 1.5 else "#FF4B4B"
    c4.markdown(f'<div style="text-align:center; background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; border: 1px solid {crv_c};"><small>CRV</small><br><span style="font-size:1.5rem; font-weight:bold; color:{crv_c};">{crv:.2f}</span></div>', unsafe_allow_html=True)

    # 6. STRATEGIE-CHECK
    st.markdown("---")
    st.subheader("🎯 Strategie-Check & Handlung")
    col_str1, col_str2 = st.columns(2)
    with col_str1:
        st.markdown(f'<div style="text-align:center; padding:20px; border:2px solid {crv_c}; border-radius:15px; background:rgba(255,255,255,0.03);"><small>CHANCE-RISIKO-SCORE</small><br><span style="font-size:2.5rem; font-weight:bold; color:{crv_c};">{crv:.2f}</span></div>', unsafe_allow_html=True)
    with col_str2:
        msg, b_clr = ("🔥 **STARKE CHANCE:** Hoher Vorteil.", "#00FFA3") if crv >= 2 and ann_vol < 35 else \
                     ("⚠️ **HOHE GEFAHR:** Markt zu unruhig.", "#FFD700") if ann_vol > 40 else \
                     ("🛑 **KEIN TRADE:** CRV zu schwach.", "#FF4B4B")
        st.markdown(f'<div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; border-left: 8px solid {b_clr}; height: 100%;">{msg}</div>', unsafe_allow_html=True)

# FOOTER
aktuelle_zeit = pd.Timestamp.now().strftime('%d.%m.%Y | %H:%M:%S')
st.info(f"🕒 Stand: {aktuelle_zeit} | 📊 Analyse: 4h-Intervall (60 Tage Historie)")
