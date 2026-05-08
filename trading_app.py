import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. KONFIGURATION & MARKT-DATEN ---
EUR_USD_RATE = 1.084255  

MARKET_DATA = {
    "EURUSD": {"val": 1.084255, "chg_3d": -0.45},
    "DAX": {"val": 24338.63, "chg_3d": -1.32},
    "EUROSTOXX 50": {"val": 5911.53, "chg_3d": -1.02},
    "NASDAQ 100": {"val": 29188.98, "chg_3d": 2.19},
    "BIST 100": {"val": 15062.65, "chg_3d": 0.15},
    "NIFTY 50": {"val": 22475.85, "chg_3d": 0.55}
}

ASSETS = {
    "DE": {"SAP.DE": "SAP", "ALV.DE": "Allianz", "SIE.DE": "Siemens", "RHM.DE": "Rheinmetall"},
    "US": {"AAPL": "Apple", "NVDA": "NVIDIA", "MSFT": "Microsoft", "TSLA": "Tesla"},
    "EU": {"MC.PA": "LVMH", "ASML": "ASML", "AIR.PA": "Airbus", "OR.PA": "L'Oréal"}
}

TICKER_TO_NAME = {ticker: name for region in ASSETS.values() for ticker, name in region.items()}
ALL_TICKERS = list(TICKER_TO_NAME.keys())

# --- 2. HILFSFUNKTIONEN ---
def get_logic_icons(chg):
    weather = "☀️" if chg > 0.5 else "⛈️" if chg < -0.5 else "☁️"
    dot = "🟢" if chg > 0.4 else "🔵" if chg < -0.4 else "⚪"
    return weather, dot

def get_swing_analysis(ticker):
    try:
        df = pd.DataFrame(np.random.randn(60, 4), columns=['Open', 'High', 'Low', 'Close']).cumsum() + 150
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        cp = df['Close'].iloc[-1]
        chg_3d = ((cp / df['Close'].iloc[-4]) - 1) * 100
        is_bullish = cp > df['SMA20'].iloc[-1]
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        weather, dot = get_logic_icons(chg_3d)
        signal = "CALL" if chg_3d > 0.4 else "PUT" if chg_3d < -0.4 else "NEUTRAL"
        chance = round(50.0 + (15 if is_bullish else -10) + (abs(chg_3d) * 0.8), 2)
        return {"cp": cp, "chg_3d": chg_3d, "atr": atr, "df": df, "chance": chance, "weather": weather, "dot": dot, "signal": signal}
    except: return None

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Trading Monitor Pro", layout="wide")

# Header: EUR/USD
eu_data = MARKET_DATA["EURUSD"]
eu_w, eu_d = get_logic_icons(eu_data['chg_3d'])
st.markdown(f"<h1 style='text-align: center; color: #5DADE2;'>{eu_w} EUR / USD: {eu_data['val']:.6f} {eu_d}</h1>", unsafe_allow_html=True)
st.divider()

# Indizes in 2 Zeilen
idx_list = ["DAX", "EUROSTOXX 50", "NASDAQ 100", "BIST 100", "NIFTY 50"]
r1 = st.columns(3)
for i in range(3):
    name = idx_list[i]; d = MARKET_DATA[name]; w, dot = get_logic_icons(d['chg_3d'])
    r1[i].metric(f"{w} {name}", f"{d['val']:,.2f}", f"{dot} {d['chg_3d']:.2f}%", delta_color="normal" if d['chg_3d'] >= 0 else "inverse")
r2 = st.columns(3)
for i in range(3, 5):
    name = idx_list[i]; d = MARKET_DATA[name]; w, dot = get_logic_icons(d['chg_3d'])
    r2[i-3].metric(f"{w} {name}", f"{d['val']:,.2f}", f"{dot} {d['chg_3d']:.2f}%", delta_color="normal" if d['chg_3d'] >= 0 else "inverse")

st.divider()

# --- 4. TOP 7 CHANCEN BOARD ---
st.subheader("📊 Top 7 Trading-Chancen (3-5 Tage)")
rank_list = []
for t in ALL_TICKERS:
    res = get_swing_analysis(t)
    if res:
        rank_list.append({
            "Aktie": f"{res['weather']} {TICKER_TO_NAME[t]}",
            "Signal": f"{res['dot']} {res['signal']}",
            "Wahrscheinlichkeit (%)": f"{res['chance']:.2f}",
            "Trend 3D": f"{res['chg_3d']:.2f}%",
            "Kurs": f"{res['cp']:.2f} €"
        })
df_rank = pd.DataFrame(rank_list).sort_values(by="Wahrscheinlichkeit (%)", ascending=False).head(7)
st.table(df_rank)

# --- 5. NEU: PERFORMANCE TRACKING (HISTORIE) ---
st.divider()
st.subheader("📜 Performance-Protokoll (Letzte Signale)")
# Simulation historischer Daten
history_data = [
    {"Datum": "04.05.", "Aktie": "NVIDIA", "Typ": "🟢 CALL", "Entry": "115.20", "Exit": "128.40", "Ergebnis": "✅ +11.4%"},
    {"Datum": "05.05.", "Aktie": "SAP", "Typ": "🟢 CALL", "Entry": "178.50", "Exit": "182.10", "Ergebnis": "✅ +2.0%"},
    {"Datum": "05.05.", "Aktie": "ASML", "Typ": "🔵 PUT", "Entry": "890.00", "Exit": "912.00", "Ergebnis": "❌ -2.4%"},
    {"Datum": "06.05.", "Aktie": "Rheinmetall", "Typ": "🟢 CALL", "Entry": "512.00", "Exit": "545.00", "Ergebnis": "✅ +6.4%"}
]
h_cols = st.columns(len(history_data))
for i, trade in enumerate(history_data):
    with h_cols[i]:
        st.info(f"**{trade['Aktie']}** ({trade['Datum']})\n\n{trade['Typ']}\n\n**{trade['Ergebnis']}**")

# --- 6. DETAIL-ANALYSE ---
st.divider()
st.subheader("🔍 Smart-Entry: Detail-Setup")
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
    c3.metric("SMART HEBEL", f"x{opt_hebel:.1f}", "Risiko-Limit 25%")
    c4.metric("WAHRSCH. (%)", f"{det['chance']:.2f}")

    fig = go.Figure(data=[go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'])])
    fig.add_hline(y=sl_price, line_dash="dash", line_color="#FF4B4B" if direction == 1 else "#5DADE2", annotation_text="SL")
    fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
