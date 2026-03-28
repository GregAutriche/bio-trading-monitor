import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60 * 1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "ADS.DE": "DE Adidas", "AIR.DE": "DE Airbus", "ALV.DE": "DE Allianz", 
    "BAS.DE": "DE BASF", "BMW.DE": "DE BMW", "DBK.DE": "DE Deutsche Bank",
    "SAP.DE": "DE SAP", "VOW3.DE": "DE VW", "EURUSD=X": "EUR/USD", "^GDAXI": "DAX 40"
}
STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k]

# --- 3. DESIGN (MAXIMALER KONTRAST) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    /* Metriken extrem scharf */
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 800 !important; color: #00FFA3 !important; }
    [data-testid="stMetricLabel"] { font-size: 0.9rem !important; color: #1E90FF !important; text-transform: uppercase; letter-spacing: 1px; }
    div[data-testid="stMetric"] { background: #161B22; border: 2px solid #30363D; padding: 15px; border-radius: 12px; }
    /* Tabellen-Kontrast */
    .stTable td { color: #FFFFFF !important; font-weight: 500 !important; background-color: #161B22 !important; border: 1px solid #30363D !important; }
    .stTable th { background-color: #1E90FF !important; color: #FFFFFF !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATEN-LOGIK ---
@st.cache_data(ttl=50)
def get_analysis(ticker_symbol):
    try:
        tk = yf.Ticker(ticker_symbol)
        df = tk.history(period="60d", interval="1d")
        if df.empty: return None
        
        cp = df["Close"].iloc[-1]
        chg = ((cp / df["Close"].iloc[-2]) - 1) * 100
        curr_vol = df["Volume"].iloc[-1]
        avg_vol = df["Volume"].tail(20).mean()
        vol_rel = curr_vol / avg_vol
        
        # ATR 14
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        
        return {"cp": cp, "chg": chg, "vol": curr_vol, "vol_rel": vol_rel, "atr": atr, "df": df, "chance": 51.0 + (vol_rel * 2)}
    except: return None

# --- 5. DASHBOARD LAYOUT ---
st.title("📊 Bio-Trading Monitor Live PRO")

# 5.1 DETAIL-ANALYSE (JETZT ALS ERSTES)
selected_ticker = st.selectbox("Wähle eine Aktie zur Volumen-Analyse:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])
data = get_analysis(selected_ticker)

if data:
    # Metriken unter der Auswahl
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("KURS", f"{data['cp']:.2f} €", f"{data['chg']:.2f}%")
    with m2: st.metric("VOLUMEN-REL", f"{data['vol_rel']:.2f}x", "vs. 20D Ø")
    with m3: st.metric("CHANCE", f"{data['chance']:.2f}%", "Vola-Score")
    with m4: st.metric("ATR (14D)", f"{data['atr']:.2f}", "Schwankung")

    # Der Volumenschart (Subplots)
    df = data["df"]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    
    # Preis oben
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Kurs"), row=1, col=1)
    # Volumen unten (Farbe je nach Kerze)
    colors = ['#00FFA3' if c >= o else '#FF4B4B' for o, c in zip(df['Open'], df['Close'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volumen"), row=2, col=1)

    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

# 5.2 TOP CHANCEN TABELLE (JETZT DARUNTER)
st.divider()
st.subheader("🚀 Top Markt-Chancen (Vola-Analyse)")

top_list = []
for t in STOCKS_ONLY:
    d = get_analysis(t)
    if d:
        top_list.append({"Aktie": TICKER_NAMES[t], "Kurs (€)": f"{d['cp']:.2f}", "Vol-Rel": f"{d['vol_rel']:.2f}x", "Chance (%)": round(d['chance'], 2)})

df_top = pd.DataFrame(top_list).sort_values(by="Chance (%)", ascending=False)
st.table(df_top) # Hoher Kontrast durch CSS oben gesichert
