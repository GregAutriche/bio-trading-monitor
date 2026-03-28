import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta

# --- 1. KONFIGURATION & REFRESH (5 MINUTEN) ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=5 * 60 * 1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
INDEX_MAPPING = {"^GDAXI": "DAX 40", "^NDX": "NASDAQ 100", "EURUSD=X": "EUR/USD", "^STOXX50E": "EuroStoxx 50", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50"}
TICKER_NAMES = {"BAS.DE": "DE BASF", "SAP.DE": "DE SAP", "AIR.DE": "DE Airbus", "DBK.DE": "DE Deutsche Bank", "ADS.DE": "DE Adidas", "BMW.DE": "DE BMW", "ALV.DE": "DE Allianz", "VOW3.DE": "DE VW"}
STOCKS_ONLY = list(TICKER_NAMES.keys())

# --- 3. DESIGN (TRADING UI) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 800 !important; color: #F8FAFC !important; }
    div[data-testid="stMetric"] { background: #1A1C24; border: 1px solid #334155; padding: 15px; border-radius: 12px; }
    .stTable td { color: #FFFFFF !important; background-color: #11141C !important; border: 1px solid #1F2937 !important; }
    .stTable th { background-color: #1E90FF !important; color: #FFFFFF !important; }
    .execution-box { background: rgba(30, 144, 255, 0.1); border: 2px solid #1E90FF; padding: 20px; border-radius: 15px; margin-top: 10px; }
    .timer-info { color: #FFD700; font-weight: bold; font-size: 1.1rem; text-align: center; padding: 5px; border: 1px solid #FFD700; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ANALYSE-FUNKTIONEN ---
@st.cache_data(ttl=290)
def get_trading_data(symbol):
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period="60d", interval="1d")
        if df.empty: return None
        cp = df["Close"].iloc[-1]
        chg = ((cp / df["Close"].iloc[-2]) - 1) * 100
        # ATR Berechnung für SL/TP
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        vol_rel = df["Volume"].iloc[-1] / df["Volume"].tail(20).mean()
        return {"cp": cp, "chg": chg, "atr": atr, "vol_rel": vol_rel, "df": df}
    except: return None

# --- 5. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5.1 HEADER: TIMER & INDIZES
now = datetime.now()
next_refresh = (now + timedelta(minutes=5 - (now.minute % 5))).replace(second=0, microsecond=0)
time_to_close = (next_refresh - now).seconds
st.sidebar.markdown(f'<div class="timer-info">⏳ Nächster Close in: {time_to_close // 60:02d}:{time_to_close % 60:02d}</div>', unsafe_allow_html=True)

idx_cols = st.columns(6)
for i, (sym, name) in enumerate(INDEX_MAPPING.items()):
    val, chg = (yf.Ticker(sym).history(period="2d")["Close"].iloc[-1], ((yf.Ticker(sym).history(period="2d")["Close"].iloc[-1] / yf.Ticker(sym).history(period="2d")["Close"].iloc[-2]) - 1) * 100)
    fmt = "{:.5f}" if "EURUSD" in sym else "{:,.2f}"
    dot = "🟢" if chg > 0.4 else "🔵" if chg < -0.4 else "⚪"
    idx_cols[i].metric(f"{dot} {name}", fmt.format(val), f"{chg:.2f}%")

st.divider()

# 5.2 DETAIL-ANALYSE MIT EXECUTION-SUPPORT
st.subheader("🔍 Smart-Entry Execution Support")
sel_stock = st.selectbox("Aktie zur Trade-Planung wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])
data = get_trading_data(sel_stock)

if data:
    # Berechnung der Handelsmarken (ATR-Logik)
    direction = 1 if data['chg'] >= 0 else -1 # 1 für Long (Call), -1 für Short (Put)
    sl = data['cp'] - (1.5 * data['atr'] * direction)
    tp1 = data['cp'] + (2.0 * data['atr'] * direction)
    tp2 = data['cp'] + (3.5 * data['atr'] * direction)
    risk_per_share = abs(data['cp'] - sl)

    col_chart, col_exec = st.columns([2, 1])

    with col_exec:
        st.markdown('<div class="execution-box">', unsafe_allow_html=True)
        st.write(f"### 🛡️ Trade-Setup: {'CALL' if direction == 1 else 'PUT'}")
        risk_input = st.number_input("Dein Risiko (€):", value=100, step=50)
        
        # Positionsgröße berechnen
        pos_size = int(risk_input / risk_per_share) if risk_per_share > 0 else 0
        
        st.write(f"**Empfohlene Stückzahl:** `{pos_size}` Aktien")
        st.divider()
        st.write(f"📍 **Entry:** {data['cp']:.2f} €")
        st.write(f"🛑 **Stop-Loss:** {sl:.2f} €")
        st.write(f"🎯 **Target 1 (CRV 2.0):** {tp1:.2f} €")
        st.write(f"🎯 **Target 2 (CRV 3.5):** {tp2:.2f} €")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chart:
        df = data['df']
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Kurs"), row=1, col=1)
        
        # Handelslinien einzeichnen
        fig.add_hline(y=sl, line_dash="dash", line_color="red", annotation_text="STOP LOSS", row=1, col=1)
        fig.add_hline(y=tp1, line_dash="dash", line_color="green", annotation_text="TARGET 1", row=1, col=1)
        fig.add_hline(y=data['cp'], line_color="white", annotation_text="ENTRY", row=1, col=1)

        v_cols = ['#00FFA3' if c >= o else '#FF4B4B' for o, c in zip(df['Open'], df['Close'])]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_cols, name="Volumen"), row=2, col=1)
        fig.update_layout(height=550, template="plotly_dark", xaxis_rangeslider_visible=False, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# 5.3 MARKT-TABELLE (UNTER DEM CHART)
st.divider()
st.subheader("📊 Markt-Übersicht & Vola-Rank")
# (Hier folgt deine bekannte Tabellen-Logik aus dem vorherigen Schritt)

# 5.3 TOP MARKT-CHANCEN TABELLE
st.subheader("📊 Top Markt-Chancen (Vola-Analyse)")
top_list = []
for t in STOCKS_ONLY:
    d = get_stock_analysis(t)
    if d:
        status_info = get_weather_and_dot(d['chg'])
        top_list.append({
            "Aktie": f"{status_info} {TICKER_NAMES[t]}",
            "Signal (C/P)": "CALL" if d['chg'] > 0.4 else "PUT" if d['chg'] < -0.4 else "NEUTRAL",
            "Chance (%)": d['chance'],
            "Kurs (€)": f"{d['cp']:.2f}",
            "Vol-Rel": f"{d['vol_rel']:.2f}x"
        })

df_top = pd.DataFrame(top_list).sort_values(by="Chance (%)", ascending=False)
df_top["Chance (%)"] = df_top["Chance (%)"].map("{:.4f}".format)
st.table(df_top)

# 5.4 DETAIL-ANALYSE CHART
st.divider()
selected = st.selectbox("🔍 Detail-Analyse wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])
det = get_stock_analysis(selected)
if det:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'], name="Kurs"), row=1, col=1)
    v_colors = ['#00FFA3' if c >= o else '#FF4B4B' for o, c in zip(det['df']['Open'], det['df']['Close'])]
    fig.add_trace(go.Bar(x=det['df'].index, y=det['df']['Volume'], marker_color=v_colors, name="Volumen"), row=2, col=1)
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
