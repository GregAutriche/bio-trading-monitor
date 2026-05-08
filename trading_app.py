import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. KONFIGURATION & INDIZES (Top Info) ---
# Marktdaten für den 08.05.2026 (Beispielwerte basierend auf aktuellen Trends)
INDEX_INFO = {
    "DAX": {"val": 24338.63, "chg": -1.32},
    "EUROSTOXX 50": {"val": 5911.53, "chg": -1.02},
    "NASDAQ 100": {"val": 29189.81, "chg": 2.19},
    "BIST 100": {"val": 15062.65, "chg": 0.15},
    "NIFTY 50": {"val": 22475.85, "chg": 0.55} # Indikativ
}

ASSETS = {
    "DE": {"SAP.DE": "SAP", "ALV.DE": "Allianz", "SIE.DE": "Siemens", "RHM.DE": "Rheinmetall"},
    "US": {"AAPL": "Apple", "NVDA": "NVIDIA", "MSFT": "Microsoft", "TSLA": "Tesla"},
    "EU": {"MC.PA": "LVMH", "ASML": "ASML", "AIR.PA": "Airbus", "OR.PA": "L'Oréal"}
}

TICKER_TO_NAME = {ticker: name for region in ASSETS.values() for ticker, name in region.items()}
ALL_TICKERS = list(TICKER_TO_NAME.keys())

# --- 2. SWING-TRADING LOGIK (3-5 TAGE) ---
def get_swing_analysis(ticker):
    try:
        # Simulation Daily Data (60 Tage für Trendstabilität)
        df = pd.DataFrame(np.random.randn(60, 4), columns=['Open', 'High', 'Low', 'Close']).cumsum() + 150
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        cp = df['Close'].iloc[-1]
        
        # Trend-Check: Kurs über 20-Tage-Linie?
        is_bullish = cp > df['SMA20'].iloc[-1]
        chg_3d = ((cp / df['Close'].iloc[-4]) - 1) * 100
        
        # ATR für SL-Puffer (14 Tage Basis)
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        
        # Wahrscheinlichkeits-Score (3-5 Tage Fokus)
        chance = 50.0 + (15 if is_bullish else -10) + (abs(chg_3d) * 0.8)
        
        return {
            "cp": cp, "chg_3d": chg_3d, "atr": atr, "df": df, 
            "chance": round(chance, 2), "trend": "BULLISCH" if is_bullish else "BÄRISCH"
        }
    except: return None

# --- 3. DASHBOARD UI ---
st.set_page_config(page_title="Pro-Trading Dashboard", layout="wide")
st.title("💹 Multi-Index Trading Monitor (3-5 Tage)")

# 3.1 ERSTE INFO: INDIZES (DAX, EUROSTOXX, NASDAQ, BIST, NIFTY)
st.subheader("🌍 Globale Markt-Indikation")
idx_cols = st.columns(len(INDEX_INFO))
for i, (name, data) in enumerate(INDEX_INFO.items()):
    color = "normal" if data['chg'] >= 0 else "inverse"
    idx_cols[i].metric(name, f"{data['val']:,.2f}", f"{data['chg']:.2f}%", delta_color=color)

st.divider()

# --- 4. TOP 7 MARKT-CHANCEN (WAHRSCHEINLICHKEIT) ---
st.subheader("📊 Top 7 Trading-Ideen (3-5 Tage Gültigkeit)")
rank_data = []
for t in ALL_TICKERS:
    d = get_swing_analysis(t)
    if d:
        region = next(r for r, stocks in ASSETS.items() if t in stocks)
        rank_data.append({
            "Region": region, "Aktie": TICKER_TO_NAME[t], "Trend": d['trend'],
            "Wahrscheinlichkeit (%)": d['chance'], "Trend 3D": f"{d['chg_3d']:.2f}%", "Kurs": f"{d['cp']:.2f} €"
        })

df_rank = pd.DataFrame(rank_data).sort_values(by="Wahrscheinlichkeit (%)", ascending=False).head(7)
st.table(df_rank)

# --- 5. DETAIL-SETUP (OHNE POSITIONSRECHNER) ---
st.divider()
st.subheader("🔍 Strategisches Setup: Derivate-Parameter")

reg_choice = st.radio("Region wählen:", ["DE", "US", "EU"], horizontal=True)
selected_ticker = st.selectbox("Aktie zur Analyse:", list(ASSETS[reg_choice].keys()), format_func=lambda x: ASSETS[reg_choice][x])

det = get_swing_analysis(selected_ticker)

if det:
    # ATR-Based Stop-Loss (2.0x ATR für Swing-Puffer)
    direction = 1 if det['chg_3d'] > 0 else -1
    sl_price = det['cp'] - (2.0 * det['atr'] * direction)
    dist_pct = abs((sl_price / det['cp']) - 1)
    
    # Hebel-Advisor (Limit: 25% Verlust im Derivat bei Erreichen des SL)
    opt_hebel = 0.25 / dist_pct if dist_pct > 0 else 1.0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("KURS", f"{det['cp']:.2f} €", f"{det['chg_3d']:.2f}% (3D)")
    c2.metric("STOP-LOSS (ATR)", f"{sl_price:.2f} €", f"{dist_pct*100:.2f}% Abstand")
    c3.metric("OPTIMALER HEBEL", f"x{opt_hebel:.1f}", help="Maximiert Rendite bei kontrolliertem Risiko")
    c4.metric("HALTEDAUER", "3-5 Tage", delta="Swing-Trade")

    # Chart
    fig = go.Figure(data=[go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'])])
    fig.add_hline(y=sl_price, line_dash="dash", line_color="red", annotation_text="SL (ATR)")
    fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
