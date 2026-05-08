import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. KONFIGURATION & MARKT-DATEN ---
EUR_USD_RATE = 1.084255  

INDEX_INFO = {
    "DAX": {"val": 24338.63, "chg": -1.32},
    "EUROSTOXX 50": {"val": 5911.53, "chg": -1.02},
    "NASDAQ 100": {"val": 29188.98, "chg": 2.19},
    "BIST 100": {"val": 15062.65, "chg": 0.15},
    "NIFTY 50": {"val": 22475.85, "chg": 0.55}
}

ASSETS = {
    "DE": {"SAP.DE": "SAP", "ALV.DE": "Allianz", "SIE.DE": "Siemens", "RHM.DE": "Rheinmetall", "DTE.DE": "Telekom"},
    "US": {"AAPL": "Apple", "NVDA": "NVIDIA", "MSFT": "Microsoft", "TSLA": "Tesla", "AMZN": "Amazon"},
    "EU": {"MC.PA": "LVMH", "ASML": "ASML", "AIR.PA": "Airbus", "OR.PA": "L'Oréal", "NESN.SW": "Nestlé"}
}

TICKER_TO_NAME = {ticker: name for region in ASSETS.values() for ticker, name in region.items()}
ALL_TICKERS = list(TICKER_TO_NAME.keys())

# --- 2. ANALYSE-LOGIK (3-5 TAGE) ---
def get_swing_analysis(ticker):
    try:
        # Simulation Daily Data
        df = pd.DataFrame(np.random.randn(60, 4), columns=['Open', 'High', 'Low', 'Close']).cumsum() + 150
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        cp = df['Close'].iloc[-1]
        
        chg_3d = ((cp / df['Close'].iloc[-4]) - 1) * 100
        is_bullish = cp > df['SMA20'].iloc[-1]
        
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        
        # Wetter & Signal Logik
        weather = "☀️" if chg_3d > 0.5 else "⛈️" if chg_3d < -0.5 else "☁️"
        dot = "🟢" if chg_3d > 0.4 else "🔵" if chg_3d < -0.4 else "⚪"
        signal = "CALL" if chg_3d > 0.4 else "PUT" if chg_3d < -0.4 else "NEUTRAL"
        
        chance = 50.0 + (15 if is_bullish else -10) + (abs(chg_3d) * 0.8)
        
        return {
            "cp": cp, "chg_3d": chg_3d, "atr": atr, "df": df, "chance": round(chance, 2),
            "weather": weather, "dot": dot, "signal": signal
        }
    except: return None

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Trading Monitor Pro", layout="wide")

# 3.1 EUR / USD (6 Nachkommastellen)
st.markdown(f"<h1 style='text-align: center; color: #5DADE2;'>EUR / USD: {EUR_USD_RATE:.6f}</h1>", unsafe_allow_html=True)
st.divider()

# 3.2 INDIZES IN 2 ZEILEN
st.subheader("🌍 Globale Markt-Indikation")
idx_keys = list(INDEX_INFO.keys())
row1 = st.columns(3)
for i in range(3):
    name = idx_keys[i]
    d = INDEX_INFO[name]
    row1[i].metric(name, f"{d['val']:,.2f}", f"{d['chg']:.2f}%", delta_color="normal" if d['chg'] >= 0 else "inverse")

row2 = st.columns(3)
for i in range(3, 5):
    name = idx_keys[i]
    d = INDEX_INFO[name]
    row2[i-3].metric(name, f"{d['val']:,.2f}", f"{d['chg']:.2f}%", delta_color="normal" if d['chg'] >= 0 else "inverse")

st.divider()

# --- 4. TOP 7 MARKT-CHANCEN (WAHRSCHEINLICHKEIT) ---
st.subheader("📊 Top 7 Trading-Chancen (3-5 Tage Gültigkeit)")
rank_list = []
for t in ALL_TICKERS:
    d = get_swing_analysis(t)
    if d:
        region = next(r for r, stocks in ASSETS.items() if t in stocks)
        rank_list.append({
            "Aktie": f"{d['weather']} {TICKER_TO_NAME[t]}",
            "Signal (C/P)": f"{d['dot']} {d['signal']}",
            "Wahrscheinlichkeit (%)": d['chance'],
            "Trend 3D": f"{d['chg_3d']:.2f}%",
            "Kurs": f"{d['cp']:.2f} €"
        })

df_rank = pd.DataFrame(rank_list).sort_values(by="Wahrscheinlichkeit (%)", ascending=False).head(7)
st.table(df_rank)

# --- 5. DETAIL-ANALYSE ---
st.divider()
st.subheader("🔍 Smart-Entry: Detail-Setup & Derivate")
reg_choice = st.radio("Region:", ["DE", "US", "EU"], horizontal=True)
selected = st.selectbox("Aktie wählen:", list(ASSETS[reg_choice].keys()), format_func=lambda x: ASSETS[reg_choice][x])

det = get_swing_analysis(selected)
if det:
    direction = 1 if det['chg_3d'] > 0 else -1
    sl_price = det['cp'] - (2.0 * det['atr'] * direction)
    dist_pct = abs((sl_price / det['cp']) - 1)
    opt_hebel = 0.25 / dist_pct if dist_pct > 0 else 1.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SIGNAL", f"{det['dot']} {det['signal']}", f"Wetter: {det['weather']}")
    c2.metric("STOP-LOSS (ATR)", f"{sl_price:.2f} €", f"{dist_pct*100:.2f}% Puffer")
    c3.metric("OPTIMALER HEBEL", f"x{opt_hebel:.1f}", "Risiko-Limit 25%")
    c4.metric("KURS", f"{det['cp']:.2f} €", f"{det['chg_3d']:.2f}% (3D)")

    # Chart
    fig = go.Figure(data=[go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'])])
    fig.add_hline(y=sl_price, line_dash="dash", line_color="#FF4B4B" if direction == 1 else "#5DADE2", annotation_text="SL")
    fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
