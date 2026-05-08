import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. AKTUELLE MARKT-DATEN (Stand: 08.05.2026) ---
# EUR/USD mit 6 Nachkommastellen
EUR_USD_RATE = 1.084255  

# Indizes für die 2-Zeilen-Ansicht
INDEX_INFO = {
    "DAX": {"val": 24338.63, "chg": -1.32},
    "EUROSTOXX 50": {"val": 5911.53, "chg": -1.02},
    "NASDAQ 100": {"val": 29188.98, "chg": 2.19},
    "BIST 100": {"val": 15062.65, "chg": 0.15},
    "NIFTY 50": {"val": 22475.85, "chg": 0.55}
}

ASSETS = {
    "DE": {"SAP.DE": "SAP", "ALV.DE": "Allianz", "SIE.DE": "Siemens", "RHM.DE": "Rheinmetall"},
    "US": {"AAPL": "Apple", "NVDA": "NVIDIA", "MSFT": "Microsoft", "TSLA": "Tesla"},
    "EU": {"MC.PA": "LVMH", "ASML": "ASML", "AIR.PA": "Airbus", "OR.PA": "L'Oréal"}
}

TICKER_TO_NAME = {ticker: name for region in ASSETS.values() for ticker, name in region.items()}
ALL_TICKERS = list(TICKER_TO_NAME.keys())

# --- 2. STABILE SWING-LOGIK (3-5 TAGE) ---
def get_swing_analysis(ticker):
    try:
        # Simulation Tagesdaten (Daily)
        df = pd.DataFrame(np.random.randn(60, 4), columns=['Open', 'High', 'Low', 'Close']).cumsum() + 150
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        cp = df['Close'].iloc[-1]
        
        is_bullish = cp > df['SMA20'].iloc[-1]
        chg_3d = ((cp / df['Close'].iloc[-4]) - 1) * 100
        
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        
        chance = 50.0 + (15 if is_bullish else -10) + (abs(chg_3d) * 0.8)
        
        return {
            "cp": cp, "chg_3d": chg_3d, "atr": atr, "df": df, 
            "chance": round(chance, 2), "trend": "BULLISCH" if is_bullish else "BÄRISCH"
        }
    except: return None

# --- 3. DASHBOARD UI ---
st.set_page_config(page_title="Pro-Trading Dashboard", layout="wide")

# 3.1 EUR / USD KURS (Zentral oben)
st.markdown(f"<h1 style='text-align: center; color: #5DADE2;'>EUR / USD: {EUR_USD_RATE:.6f}</h1>", unsafe_allow_html=True)
st.divider()

# 3.2 GLOBALE INDIZES IN 2 ZEILEN
st.subheader("🌍 Globale Markt-Indikation")
# Zeile 1: DAX, EUROSTOXX, NASDAQ
idx_keys = list(INDEX_INFO.keys())
row1 = st.columns(3)
for i in range(3):
    name = idx_keys[i]
    data = INDEX_INFO[name]
    row1[i].metric(name, f"{data['val']:,.2f}", f"{data['chg']:.2f}%", delta_color="normal" if data['chg'] >= 0 else "inverse")

# Zeile 2: BIST, NIFTY
row2 = st.columns(3) # 3 Spalten für Layout-Konsistenz
for i in range(3, 5):
    name = idx_keys[i]
    data = INDEX_INFO[name]
    row2[i-3].metric(name, f"{data['val']:,.2f}", f"{data['chg']:.2f}%", delta_color="normal" if data['chg'] >= 0 else "inverse")

st.divider()

# --- 4. TOP 7 MARKT-CHANCEN ---
st.subheader("📊 Top 7 Trading-Ideen (3-5 Tage)")
rank_data = []
for t in ALL_TICKERS:
    d = get_swing_analysis(t)
    if d:
        region = next(r for r, stocks in ASSETS.items() if t in stocks)
        rank_data.append({
            "Region": region, "Aktie": TICKER_TO_NAME[t], "Trend": d['trend'],
            "Chance (%)": d['chance'], "Trend 3D": f"{d['chg_3d']:.2f}%", "Kurs": f"{d['cp']:.2f} €"
        })

df_rank = pd.DataFrame(rank_data).sort_values(by="Chance (%)", ascending=False).head(7)
st.table(df_rank)

# --- 5. DETAIL-SETUP ---
st.divider()
st.subheader("🔍 Strategisches Setup: Derivate-Parameter")

reg_choice = st.radio("Region wählen:", ["DE", "US", "EU"], horizontal=True)
selected_ticker = st.selectbox("Aktie zur Analyse:", list(ASSETS[reg_choice].keys()), format_func=lambda x: ASSETS[reg_choice][x])

det = get_swing_analysis(selected_ticker)

if det:
    direction = 1 if det['chg_3d'] > 0 else -1
    sl_price = det['cp'] - (2.0 * det['atr'] * direction)
    dist_pct = abs((sl_price / det['cp']) - 1)
    
    # Hebel-Advisor
    opt_hebel = 0.25 / dist_pct if dist_pct > 0 else 1.0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("KURS", f"{det['cp']:.2f} €")
    c2.metric("STOP-LOSS", f"{sl_price:.2f} €", f"{dist_pct*100:.2f}% Abstand")
    c3.metric("SMART HEBEL", f"x{opt_hebel:.1f}")
    c4.metric("DAUER", "3-5 Tage")

    # Chart
    fig = go.Figure(data=[go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'])])
    fig.add_hline(y=sl_price, line_dash="dash", line_color="red", annotation_text="SL")
    fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
