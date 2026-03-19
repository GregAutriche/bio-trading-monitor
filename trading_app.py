import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. VOLLSTÄNDIGES NAMENS-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50",
    "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer",
    "BMW.DE": "BMW", "DBK.DE": "Deutsche Bank", "DTE.DE": "Telekom", "SAP.DE": "SAP", "SIE.DE": "Siemens",
    "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "RHM.DE": "Rheinmetall", "VOW3.DE": "Volkswagen",
    "AAPL": "Apple", "NVDA": "Nvidia", "TSLA": "Tesla", "MSFT": "Microsoft", "AMZN": "Amazon",
    "THYAO.IS": "Turkish Airlines", "RELIANCE.NS": "Reliance Ind."
}

TICKER_GROUPS = {
    "DAX 40 (DE)": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "ADS.DE", "BMW.DE", "BAYN.DE", "BAS.DE", "DBK.DE", "RHM.DE", "IFX.DE", "MBG.DE"],
    "EuroStoxx 50 (EU)": ["AIR.PA", "MC.PA", "OR.PA", "ASML.AS", "SAN.PA", "BNP.PA", "TTE.PA", "ITX.MC"],
    "NASDAQ 100 (US)": ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "META", "GOOGL", "AMD", "NFLX"],
    "BIST 100 (TR)": ["THYAO.IS", "ASELS.IS", "KCHOL.IS"],
    "Nifty 50 (IN)": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; color: white; }
    .bullish { color: #00FFA3; font-weight: bold; }
    .bearish { color: #FF4B4B; font-weight: bold; }
    .header-box { background: rgba(30,144,255,0.1); padding: 15px; border-radius: 12px; border: 1px solid #1E90FF; text-align: center; margin-bottom: 20px; }
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

def run_market_scanner(ticker_list):
    results = []
    for t in ticker_list:
        df = get_data(t, period="5d")
        if not df.empty and len(df) >= 2:
            cp = float(df['Close'].iloc[-1].values) if hasattr(df['Close'].iloc[-1], 'values') else float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2].values) if hasattr(df['Close'].iloc[-2], 'values') else float(df['Close'].iloc[-2])
            trend = ((cp / prev) - 1) * 100
            results.append({"Aktie": TICKER_NAMES.get(t, t), "Kurs": round(cp, 2), "Trend %": round(trend, 2)})
    return pd.DataFrame(results)

# --- 5. HEADER: ZEILE 1 (WÄHRUNGEN) ---
st.title("🚀 Bio-Trading Monitor Live PRO")
st.subheader("💱 Währungen")
cf1, cf2, _ = st.columns(3)
for i, t in enumerate(["EURUSD=X", "EURRUB=X"]):
    df_f = get_data(t, period="2d")
    if not df_f.empty:
        l = float(df_f['Close'].iloc[-1].values) if hasattr(df_f['Close'].iloc[-1], 'values') else float(df_f['Close'].iloc[-1])
        c = ((l / (float(df_f['Close'].iloc[-2].values) if hasattr(df_f['Close'].iloc[-2], 'values') else float(df_f['Close'].iloc[-2]))) - 1) * 100
        (cf1 if i==0 else cf2).markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.5f}</span> <span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

# --- ZEILE 2 (INDIZES) ---
st.subheader("📈 Markt-Indizes")
cols_i = st.columns(5)
for i, t in enumerate(["^GDAXI", "^STOXX50E", "^NDX", "XU100.IS", "^NSEI"]):
    df_i = get_data(t, period="2d")
    if not df_i.empty:
        l = float(df_i['Close'].iloc[-1].values) if hasattr(df_i['Close'].iloc[-1], 'values') else float(df_i['Close'].iloc[-1])
        c = ((l / (float(df_i['Close'].iloc[-2].values) if hasattr(df_i['Close'].iloc[-2], 'values') else float(df_i['Close'].iloc[-2]))) - 1) * 100
        cols_i[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.2f}</span> <span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

st.divider()

# --- 6. MONTE CARLO PROGNOSE & BIO-WETTER LOGIK ---
if 'sel_market' not in st.session_state: st.session_state.sel_market = "DAX 40 (DE)"
if 'sel_stock' not in st.session_state: st.session_state.sel_stock = "SAP.DE"

d_s = get_data(st.session_state.sel_stock)
if not d_s.empty:
    # Daten sicher als Float laden
    cp = float(d_s['Close'].iloc[-1].values) if hasattr(d_s['Close'].iloc[-1], 'values') else float(d_s['Close'].iloc[-1])
    
    # --- BERECHNUNG WETTER & AKTION (C/P) ---
    trend_5d = ((cp / d_s['Close'].iloc[-5]) - 1) * 100
    target_val = cp * 1.05
    sl_val = cp * 0.97
    sl_dist = ((sl_val / cp) - 1) * 100

    # Logik: Call (C) bei Sonne/Grün, Put (P) bei Regen/Rot
    if trend_5d > 0:
        aktion = "(C) Ziel:"
        wetter_icon = "☀️"
        color_hex = "#00FFA3" # Bullish Green
    else:
        aktion = "(P) Ziel:"
        wetter_icon = "⛈️"
        color_hex = "#FF4B4B" # Bearish Red

    # DER FINALE FOKUS-BALKEN (Wie im Screenshot)
    st.markdown(f"""
        <div style="background: rgba(30,144,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid #1E90FF; text-align: center; margin-bottom: 25px;">
            <span style="color:#8892b0; font-size:0.9rem;">Fokus:</span> 
            <b style="font-size:1.2rem; color:white; margin-left:5px;">{TICKER_NAMES.get(st.session_state.sel_stock, st.session_state.sel_stock)}</b> 
            <span style="color:#1E90FF; margin: 0 20px;">|</span>
            <span style="color:#8892b0; font-size:0.9rem;">Kurs:</span> 
            <b style="font-size:1.2rem; color:white; margin-left:5px;">{cp:,.2f}</b> 
            <span style="color:#1E90FF; margin: 0 20px;">|</span>
            <span style="color:{color_hex}; font-weight:bold; font-size:1.2rem;">
                {aktion} {target_val:,.2f} 
                <span style="font-size:0.9rem; color:#8892b0; font-weight:normal; margin-left:5px;">({sl_dist:+.2f}% SL)</span> 
                <span style="margin-left:8px;">{wetter_icon}</span>
            </span>
        </div>
    """, unsafe_allow_html=True)

    # --- MONTE CARLO CHART ---
    # (Hier folgt dein bisheriger Plot-Code...)

    # --- MONTE CARLO CHART ---
    st.subheader(f"🔮 Prognose-Wetter: {TICKER_NAMES.get(st.session_state.sel_stock, st.session_state.sel_stock)}")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 4.5))
    fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
    
    log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)); vol = log_returns.std()
    for _ in range(25):
        p = [cp]
        for _ in range(20): p.append(p[-1] * np.exp(np.random.normal(0, vol)))
        ax.plot(p, color='#00FFA3' if p[-1] > cp else '#FF4B4B', alpha=0.15)
    
    ax.axhline(y=cp, color='white', linestyle='--', alpha=0.3)
    ax.axhline(y=target_val, color='#1E90FF', linestyle=':', alpha=0.6)
    st.pyplot(fig)

# --- 7. SCANNER (DARUNTER) ---
st.subheader(f"🎯 Scanner: {st.session_state.sel_market}")
with st.spinner("Scanne Markt-Signale..."):
    scan_results = run_market_scanner(TICKER_GROUPS[st.session_state.sel_market])
    if not scan_results.empty:
        col_c, col_p = st.columns(2)
        with col_c:
            st.markdown("<span class='bullish'>🟢 TOP 5 CALLS</span>", unsafe_allow_html=True)
            st.dataframe(scan_results.sort_values(by="Trend %", ascending=False).head(5), use_container_width=True, hide_index=True)
        with col_p:
            st.markdown("<span class='bearish'>🔴 TOP 5 PUTS</span>", unsafe_allow_html=True)
            st.dataframe(scan_results.sort_values(by="Trend %", ascending=True).head(5), use_container_width=True, hide_index=True)

# --- 8. STEUERUNG (GANZ UNTEN) ---
st.divider()
st.subheader("⚙️ Auswahl & Steuerung")
cs1, cs2 = st.columns(2)
# Speichern der Auswahl direkt in den Session State
st.session_state.sel_market = cs1.selectbox("1. Index wählen:", list(TICKER_GROUPS.keys()), index=list(TICKER_GROUPS.keys()).index(st.session_state.sel_market))
# Sicherstellen, dass der gewählte Stock auch im gewählten Markt existiert
valid_stocks = TICKER_GROUPS[st.session_state.sel_market]
default_stock_index = valid_stocks.index(st.session_state.sel_stock) if st.session_state.sel_stock in valid_stocks else 0
st.session_state.sel_stock = cs2.selectbox("2. Aktie wählen:", valid_stocks, index=default_stock_index, format_func=lambda x: TICKER_NAMES.get(x, x))
