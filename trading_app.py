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
    # EURO STOXX 50 & DAX (Auswahl)
    "ASML.AS": "ASML", "MC.PA": "LVMH", "SAP.DE": "SAP", "OR.PA": "L'Oréal", "ADS.DE": "Adidas", 
    "AIR.PA": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer", "BMW.DE": "BMW",
    "DHL.DE": "DHL Group", "DTE.DE": "Telekom", "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz",
    "MRK.DE": "Merck", "MUV2.DE": "Münchener Rück", "RHM.DE": "Rheinmetall", "SIE.DE": "Siemens",
    "VOW3.DE": "Volkswagen", "VNA.DE": "Vonovia", "CBK.DE": "Commerzbank",
    # NASDAQ
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "AMZN": "Amazon", "META": "Meta", "TSLA": "Tesla",
    "GOOGL": "Alphabet", "AVGO": "Broadcom", "COST": "Costco", "NFLX": "Netflix", "AMD": "AMD"
}

TICKER_GROUPS = {
    "EuroStoxx 50 (EU)": ["ASML.AS", "MC.PA", "SAP.DE", "OR.PA", "AIR.PA", "DHL.DE", "BNP.PA", "ITX.MC", "SAN.MC", "EL.PA"],
    "DAX 40 (DE)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
    "NASDAQ 100 (US)": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", "NFLX", "AMD"]
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; color: white; }
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

def draw_info_card(col, t, is_currency=False):
    df = get_data(t, period="5d")
    if not df.empty:
        l = extract_price(df, -1); p = extract_price(df, -2); diff = ((l/p)-1)*100
        prec = 4 if is_currency else 2
        if diff > 0.15: sig, icon, clr = "CALL (STARK)", "☀️", "#00FFA3"
        elif diff < -0.15: sig, icon, clr = "PUT (BEARISH)", "⛈️", "#FF4B4B"
        else: sig, icon, clr = "NEUTRAL", "⛅", "#8892b0"
        col.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between;">
                    <small style="color:#8892b0;">{TICKER_NAMES.get(t,t)}</small>
                    <span style="color:{clr} !important; font-size:1.2rem;">{icon}</span>
                </div>
                <div class="metric-value" style="margin: 5px 0;">{l:,.{prec}f}</div>
                <div style="color:{clr} !important; font-weight: bold; font-size: 0.85rem;">{sig} ({diff:+.2f}%)</div>
            </div>
        """, unsafe_allow_html=True)

def run_market_scanner(ticker_list):
    results = []
    data = yf.download(ticker_list, period="60d", interval="4h", progress=False)
    if isinstance(data.columns, pd.MultiIndex): close_p = data['Close']
    else: close_p = data[['Close']]
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

# --- 5. AUFBAU ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# A. WÄHRUNGEN
st.subheader("💱 Fokus/ Währungen")
cw1, cw2, _ = st.columns(3)
draw_info_card(cw1, "EURUSD=X", True); draw_info_card(cw2, "EURRUB=X", True)

# B. INDIZES (2 ZEILEN)
st.subheader("📈 Fokus/ Indizes")
c_r1 = st.columns(2); draw_info_card(c_r1[0], "^GDAXI"); draw_info_card(c_r1[1], "^NDX")
c_r2 = st.columns(3); draw_info_card(c_r2[0], "^STOXX50E"); draw_info_card(c_r2[1], "XU100.IS"); draw_info_card(c_r2[2], "^NSEI")

st.divider()

# C. STEUERUNG (ALPHABETISCH)
cs1, cs2 = st.columns(2)
sel_market = cs1.selectbox("Markt wählen:", list(TICKER_GROUPS.keys()))
sorted_stocks = sorted(TICKER_GROUPS[sel_market], key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = cs2.selectbox("Aktie wählen:", sorted_stocks, format_func=lambda x: TICKER_NAMES.get(x, x))

# D. SCANNER (NUR PUNKTE)
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

# E. MARKT-AMPEL
ist_we = pd.Timestamp.now().weekday() >= 5
m_clr = "#FF4B4B" if ist_we else "#00FFA3"
m_txt = "🛑 GESCHLOSSEN (Wochenende)" if ist_we else "🟢 GEÖFFNET (Live-Handel)"
st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:10px; border-radius:10px; border-left: 5px solid {m_clr}; margin: 20px 0; color:white;">{m_txt}</div>', unsafe_allow_html=True)

st.divider()

# F. ANALYSE & SETUP (MIT VOLUMEN)
d_s = get_data(sel_stock, period="60d")
if not d_s.empty:
    log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)).dropna()
    vol = log_returns.std(); ann_vol = vol * np.sqrt(252) * 100; cp = extract_price(d_s, -1)
    
    # Volumen-Logik
    avg_vol = d_s['Volume'].tail(10).mean(); cur_vol = d_s['Volume'].iloc[-1]
    v_diff = ((cur_vol / avg_vol) - 1) * 100 if avg_vol > 0 else 0
    v_icon, v_col = ("🔥", "#00FFA3") if v_diff > 15 else ("💤", "#FF4B4B") if v_diff < -15 else ("📊", "#8892b0")

    np.random.seed(int(pd.Timestamp.now().timestamp() // 86400) + hash(sel_stock) % 1000)
    sim_results = [cp * np.exp(np.random.normal(0, vol * np.sqrt(15))) for _ in range(100)]
    is_long = bool(np.median(sim_results) >= cp)
    t_up, t_down = np.percentile(sim_results, 95), np.percentile(sim_results, 5)
    sig_t, sig_i, sig_c = ("LONG EINSTIEG", "🟢", "#00FFA3") if is_long and ann_vol < 35 else ("SHORT CHANCE", "🔴", "#FF4B4B") if not is_long and ann_vol < 35 else ("ABWARTEN", "⚪", "#8892b0")
    
    st.markdown(f'<div class="header-box" style="border-color:{sig_c};"><b>{TICKER_NAMES.get(sel_stock, sel_stock)}</b> | Vola: <b>{ann_vol:.1f}%</b> | Volumen: <b style="color:{v_col};">{v_icon} {v_diff:+.1f}%</b></div>', unsafe_allow_html=True)
    
    dir_label, dir_col = ("[ CALL ]", "#00FFA3") if is_long else ("[ PUT ]", "#FF4B4B")
    st.markdown(f"### 📝 Handels-Setup: <span style='color:{dir_col} !important;'>{dir_label}</span> <span style='float:right; font-size:1rem; color:{sig_c} !important;'>{sig_i} {sig_t}</span>", unsafe_allow_html=True)
    
    target_p = t_up if is_long else t_down; stop_l = cp * 0.97 if is_long else cp * 1.03
    risk = abs(cp - stop_l); reward = abs(target_p - cp); crv = reward / risk if risk > 0 else 0
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("EINSTIEG", f"{cp:,.2f}")
    c2.metric("ZIEL (TP)", f"{target_p:,.2f}", f"{(target_p/cp-1)*100:+.2f}%", delta_color="normal" if is_long else "inverse")
    c3.metric("STOP LOSS", f"{stop_l:,.2f}", f"{(stop_l/cp-1)*100:+.2f}%", delta_color="inverse" if is_long else "normal")
    c4.metric("VOLUMEN", f"{v_icon} {v_diff:+.1f}%", "Bestätigt" if v_diff > 15 else "Schwach")
    crv_col = "#00FFA3" if crv >= 2 else "#FFD700" if crv >= 1.5 else "#FF4B4B"
    c5.markdown(f'<div style="text-align:center; background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; border: 1px solid {crv_col};"><small>CRV</small><br><span style="font-size:1.5rem; font-weight:bold; color:{crv_col};">{crv:.2f}</span></div>', unsafe_allow_html=True)

    # G. RISIKO-RADAR (FALLBACK-FIX)
    st.divider(); st.subheader("🚨 Risiko-Radar: Termine & News")
    t_obj = yf.Ticker(sel_stock); col_r1, col_r2 = st.columns(2)
    with col_r1:
        try:
            cal = t_obj.calendar
            if isinstance(cal, pd.DataFrame) and not cal.empty:
                e_date = cal.iloc[0, 0] if 'Earnings Date' in cal.index else cal.iloc[0]
                st.warning(f"Earnings am: **{pd.to_datetime(e_date).strftime('%d.%m.%Y')}**")
            else: st.info("Keine Termine.")
        except: st.info("Earnings n.v.")
    with col_r2:
        try:
            for n in t_obj.news[:3]: st.markdown(f"🔹 **{n['title']}** ([Link]({n['link']}))")
        except:
            google_url = f"https://www.google.com{TICKER_NAMES.get(sel_stock, sel_stock).replace(' ', '+')}+Aktie+News&tbm=nws"
            st.markdown(f'<a href="{google_url}" target="_blank" style="color:#1E90FF;">🔍 News auf Google prüfen</a>', unsafe_allow_html=True)

# FOOTER
st.info(f"🕒 Stand: {pd.Timestamp.now().strftime('%d.%m.%Y | %H:%M:%S')} | 📊 Analyse: 4h-Intervall (60d)")
