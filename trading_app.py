import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 1. KONFIGURATION & REFRESH (5 MINUTEN) ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
# Intervall: 5 * 60 * 1000 = 300.000 ms
st_autorefresh(interval=5 * 60 * 1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "BAS.DE": "DE BASF", "SAP.DE": "DE SAP", "AIR.DE": "DE Airbus", 
    "DBK.DE": "DE Deutsche Bank", "ADS.DE": "DE Adidas", "BMW.DE": "DE BMW",
    "ALV.DE": "DE Allianz", "VOW3.DE": "DE VW"
}
STOCKS_ONLY = list(TICKER_NAMES.keys())

# --- 3. DESIGN (KONTRAST & TABELLEN-STYLING) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .update-info { font-size: 1rem; color: #1E90FF; margin-bottom: 20px; font-weight: bold; }
    
    /* Tabellen-Styling nach Vorlage */
    .stTable td { 
        color: #FFFFFF !important; 
        background-color: #11141C !important; 
        border: 1px solid #1F2937 !important; 
        font-family: 'Courier New', monospace;
    }
    .stTable th { 
        background-color: #1E90FF !important; 
        color: #FFFFFF !important; 
        font-weight: bold !important; 
        text-align: left !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ANALYSE-FUNKTION ---
@st.cache_data(ttl=290) # TTL knapp unter dem Refresh-Intervall
def get_analysis(ticker_symbol):
    try:
        tk = yf.Ticker(ticker_symbol)
        df = tk.history(period="60d", interval="1d")
        if df.empty: return None
        
        cp = df["Close"].iloc[-1]
        chg = ((cp / df["Close"].iloc[-2]) - 1) * 100
        vol_rel = df["Volume"].iloc[-1] / df["Volume"].tail(20).mean()
        
        # Chance-Logik mit 4 Nachkommastellen Simulation
        base_chance = 52.0000 + (vol_rel * 1.5) + (abs(chg) * 0.4)
        
        return {
            "cp": cp, 
            "chg": chg, 
            "vol_rel": vol_rel, 
            "df": df, 
            "chance": round(base_chance, 4)
        }
    except: return None

# --- 5. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5.1 UPDATE-INFO (GANZ OBEN)
now = datetime.now().strftime('%H:%M:%S')
st.markdown(f'<div class="update-info">🕒 Letztes Update: {now} | Aktualisierung alle: 5 Min. | Status: 🟢 Synchronisiert</div>', unsafe_allow_html=True)

# 5.2 TOP MARKT-CHANCEN (TABELLE DIREKT UNTER DER ÜBERSCHRIFT)
st.subheader("📊 Top Markt-Chancen (Vola-Analyse)")

top_list = []
for t in STOCKS_ONLY:
    d = get_analysis(t)
    if d:
        signal = "🟢 CALL" if d['chg'] >= 0 else "🔵 PUT"
        top_list.append({
            "Aktie": TICKER_NAMES[t],
            "Signal (C/P)": signal,
            "Chance (%)": d['chance'], # Numerisch für die Sortierung
            "Kurs (€)": f"{d['cp']:.2f}",
            "Vol-Rel": f"{d['vol_rel']:.2f}x"
        })

# DataFrame erstellen und AUTOMATISCH nach Chance sortieren (Absteigend)
df_top = pd.DataFrame(top_list).sort_values(by="Chance (%)", ascending=False)

# Formatierung für die Anzeige (4 Nachkommastellen fixieren)
df_top["Chance (%)"] = df_top["Chance (%)"].map("{:.4f}".format)

# Anzeige als statische Tabelle für maximalen Kontrast
st.table(df_top)

# 5.3 DETAIL-ANALYSE & VOLUMENSCHART (DARUNTER)
st.divider()
st.subheader("🔍 Detail-Analyse & Volumen-Trend")
selected_ticker = st.selectbox("Aktie wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])
detail_data = get_analysis(selected_ticker)

if detail_data:
    df = detail_data["df"]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name="Kurs",
        increasing_line_color='#00FFA3', decreasing_line_color='#FF4B4B'
    ), row=1, col=1)
    
    # Volumen farbig markieren
    v_colors = ['#00FFA3' if c >= o else '#FF4B4B' for o, c in zip(df['Open'], df['Close'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_colors, name="Volumen", opacity=0.8), row=2, col=1)

    fig.update_layout(height=550, template="plotly_dark", xaxis_rangeslider_visible=False, showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
