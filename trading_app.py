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
# 1. WÄHRUNGEN MIT SIGNAL
st.subheader("💱 Fokus/ Währungen 💱")
cf1, cf2, _ = st.columns(3)
for i, t in enumerate(["EURUSD=X", "EURRUB=X"]):
    df_f = get_data(t, period="5d")
    if not df_f.empty:
        l = extract_price(df_f, -1)
        p = extract_price(df_f, -2)
        diff = ((l/p)-1)*100
        # Signal-Logik
        sig = "STARK" if diff > 0.1 else "SCHWACH" if diff < -0.1 else "NEUTRAL"
        sig_clr = "#00FFA3" if diff > 0.1 else "#FF4B4B" if diff < -0.1 else "#8892b0"
        
        (cf1 if i==0 else cf2).markdown(f"""
            <div class="market-card">
                <small>{TICKER_NAMES.get(t,t)}</small><br>
                <span class="metric-value">{l:,.4f}</span> 
                <span style="color:{sig_clr}; font-size:0.8rem; float:right;">{sig} ({diff:+.2f}%)</span>
            </div>
        """, unsafe_allow_html=True)

# 2. INDIZES
st.subheader("📈 Fokus/ Indizes📈")
cols_i = st.columns(5)
for i, t in enumerate(["^GDAXI", "^STOXX50E", "^NDX", "XU100.IS", "^NSEI"]):
    df_i = get_data(t, period="2d")
    if not df_i.empty:
        l = extract_price(df_i, -1); p = extract_price(df_i, -2); c = ((l/p)-1)*100
        cols_i[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.2f}</span><br><span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

st.divider()

# 3. STEUERUNG
st.subheader("⚙️ Fokus/ Steuerung ⚙️")
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

# --- 5. FOKUS: TRADE-SIGNALE & MONTE CARLO ---
d_s = get_data(sel_stock, period="60d")
if not d_s.empty:
    # 1. Analyse-Metriken
    log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)).dropna()
    vol = log_returns.std()
    ann_vol = vol * np.sqrt(252) * 100
    cp = extract_price(d_s, -1)
    prev_p = extract_price(d_s, -2)
    trend = ((cp / prev_p) - 1) * 100

    # 2. Smart-Signal Logik (Trend + Risiko)
    if trend > 0.5 and ann_vol < 25:
        sig_text, sig_icon, sig_col = "LONG EINSTIEG", "🟢", "#00FFA3"
        action_hint = "Stabiler Aufwärtstrend bei niedriger Vola."
    elif trend < -0.5 and ann_vol > 30:
        sig_text, sig_icon, sig_col = "STOP-LOSS ENGER", "⚠️", "#FF4B4B"
        action_hint = "Hohe Volatilität im Abwärtstrend! Risiko minimieren."
    elif trend < -0.5:
        sig_text, sig_icon, sig_col = "SHORT CHANCE", "🔴", "#FF4B4B"
        action_hint = "Bärisches Momentum bestätigt."
    else:
        sig_text, sig_icon, sig_col = "ABWARTEN / NEUTRAL", "⚪", "#8892b0"
        action_hint = "Kein klares Signal. Markt beobachtet Seitwärtsphase."

    # 3. Monte Carlo Simulation (95% Korridor)
    n_sims = 40
    sim_results = []
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
    
    for _ in range(n_sims):
        prices = [cp]
        for _ in range(15): prices.append(prices[-1] * np.exp(np.random.normal(0, vol)))
        sim_results.append(prices[-1])
        ax.plot(prices, color=sig_col, alpha=0.1)

    t_up, t_down = np.percentile(sim_results, 95), np.percentile(sim_results, 5)

    # 4. Aktions-Info Bar (Modernes Design)
    st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; border-left: 5px solid {sig_col}; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color:{sig_col}; font-size: 1.4rem; font-weight: bold;">{sig_icon} {sig_text}</span><br>
                    <small style="color: #8892b0;">{action_hint}</small>
                </div>
                <div style="text-align: right;">
                    <span style="color: #8892b0; font-size: 0.8rem;">ZIELBEREICH (15D)</span><br>
                    <b style="color: white; font-size: 1.1rem;">{t_down:,.2f} — {t_up:,.2f}</b>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    ax.axhline(t_up, color='#00FFA3', linestyle='--', alpha=0.3)
    ax.axhline(t_down, color='#FF4B4B', linestyle='--', alpha=0.3)
    st.pyplot(fig)

    # --- 6. NEU: ORDER-BOARD (CRV RECHNER) ---
        is_long = trend >= 0
    direction_label = "[ CALL / LONG ]" if is_long else "[ PUT / SHORT ]"
    direction_col = "#00FFA3" if is_long else "#FF4B4B"
    st.markdown(f"### 📝 Handels-Setup: <span style='color:{direction_col};'>{direction_label}</span>", unsafe_allow_html=True)
    st.subheader("📝 Handels-Setup (Vorschlag)")
    
    # Dynamisches Setup basierend auf der Simulation
    if trend >= 0: # Long Szenario
        entry = cp
        target_price = t_up # 95% Quantil als Ziel
        stop_loss = cp * 0.97 # 3% Sicherheitsnetz
    else: # Short Szenario
        entry = cp
        target_price = t_down # 5% Quantil als Ziel
        stop_loss = cp * 1.03 # 3% Sicherheitsnetz oben
    
    # CRV Berechnung: (Ziel - Einstieg) / (Einstieg - Stop)
    risk = abs(entry - stop_loss)
    reward = abs(target_price - entry)
    crv = reward / risk if risk > 0 else 0
    
    # Optische Aufbereitung in 3 Spalten
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EINSTIEG (Limit)", f"{entry:,.2f}")
    c2.metric("ZIEL (Take Profit)", f"{target_price:,.2f}", f"{(target_price/entry-1)*100:+.2f}%")
    c3.metric("STOP LOSS", f"{stop_loss:,.2f}", f"{(stop_loss/entry-1)*100:+.2f}%", delta_color="inverse")
    
    # CRV Anzeige mit Farblogik
    crv_col = "#00FFA3" if crv >= 2 else "#FFD700" if crv >= 1.5 else "#FF4B4B"
    c4.markdown(f"""
        <div style="text-align:center; background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; border: 1px solid {crv_col};">
            <small style="color:#8892b0;">CHANCE-RISIKO (CRV)</small><br>
            <span style="font-size:1.5rem; font-weight:bold; color:{crv_col};">{crv:.2f}</span>
        </div>
    """, unsafe_allow_html=True)

    if crv < 1.5:
        st.warning("⚠️ CRV ist niedrig. Warte auf einen besseren Rücksetzer für den Einstieg.")
    elif crv >= 2:
        st.success("✅ Statistisch attraktives Setup erkannt.")


# --- Ganz unten in deinem Code (Abschnitt 8 / Footer) ---
st.info(f"Update: {pd.Timestamp.now().strftime('%H:%M:%S')} | Status: {TICKER_NAMES.get(sel_stock, sel_stock)}")
