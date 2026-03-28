import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
# Auto-Refresh alle 60 Sekunden
count = st_autorefresh(interval=60 * 1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    # Indizes & Forex
    "EURUSD=X": "💱 EUR/USD", "^GDAXI": "📊 DAX 40", "^NDX": "📊 NASDAQ 100",
    # Aktien DAX 40 (Beispielauswahl)
    "ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", 
    "BAS.DE": "🇩🇪 BASF", "BMW.DE": "🇩🇪 BMW", "DBK.DE": "🇩🇪 Deutsche Bank",
    "SAP.DE": "🇩🇪 SAP", "VOW3.DE": "🇩🇪 VW"
}

STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k]

# --- 3. DESIGN (DARK MODE & KONTRAST) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 800 !important; color: #FFFFFF !important; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; color: #8892b0 !important; text-transform: uppercase; }
    div[data-testid="stMetric"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; }
    .update-info { font-size: 0.8rem; color: #666; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ANALYSE-FUNKTION ---
@st.cache_data(ttl=50)
def get_analysis(ticker_symbol):
    res = {"cp": 0, "chg": 0, "atr": 0, "vol": 0, "vol_rel": 0, "chance": 50.0, "df": None}
    try:
        tk = yf.Ticker(ticker_symbol)
        # 60 Tage Daten für gleitende Durchschnitte und ATR
        df = tk.history(period="60d", interval="1d")
        
        if not df.empty and len(df) > 20:
            cp = float(df["Close"].iloc[-1])
            prev_cp = float(df["Close"].iloc[-2])
            chg = ((cp / prev_cp) - 1) * 100
            
            # Volumen-Metriken
            curr_vol = float(df["Volume"].iloc[-1])
            avg_vol = float(df["Volume"].tail(20).mean())
            vol_rel = (curr_vol / avg_vol) if avg_vol > 0 else 1.0
            
            # ATR (14 Tage)
            df['TR'] = np.maximum(df['High'] - df['Low'], 
                       np.maximum(abs(df['High'] - df['Close'].shift(1)), 
                       abs(df['Low'] - df['Close'].shift(1))))
            atr = float(df['TR'].tail(14).mean())
            
            # Chance-Simulations-Dummy (51-59%)
            chance = 51.0 + (min(abs(chg), 5)) + (min(vol_rel, 3))
            
            res.update({
                "cp": cp, "chg": chg, "atr": atr, 
                "vol": curr_vol, "vol_rel": vol_rel,
                "chance": round(min(chance, 59.9), 2),
                "df": df
            })
    except Exception as e:
        print(f"Error {ticker_symbol}: {e}")
    return res

# --- 5. DASHBOARD AUFBAU ---
st.title("📊 Bio-Trading Monitor Live PRO")
now_fixed = (datetime.now() + timedelta(hours=0)).strftime('%H:%M:%S')

st.markdown(f'<div class="update-info">🕒 Letztes Update: <b>{now_fixed}</b> | Intervall: 60s</div>', unsafe_allow_html=True)

# Detail-Analyse Auswahl
st.subheader("🔍 Detail-Analyse & Volumenschart")
selected_ticker = st.selectbox("Aktie zur Analyse wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])

data = get_analysis(selected_ticker)

if data["df"] is not None:
    # --- METRIKEN ZEILE ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("KURS", f"{data['cp']:.2f} €", f"{data['chg']:.2f}%")
    with m2:
        st.metric("STAT. CHANCE", f"{data['chance']}%", "Simulation")
    with m3:
        st.metric("VOLUMEN (REL)", f"{data['vol_rel']:.2f}x", f"{data['vol']:,.0f}")
    with m4:
        st.metric("ATR (14D)", f"{data['atr']:.2f}", "Vola")

    # --- VOLUMENSCHART (SUBPLOTS) ---
    df = data["df"]
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.08, 
        row_heights=[0.7, 0.3],
        subplot_titles=("", "HANDELSVOLUMEN")
    )

    # Kurs (Candlesticks)
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name="Kurs",
        increasing_line_color='#00FFA3', decreasing_line_color='#FF4B4B'
    ), row=1, col=1)

    # Volumen (Balken farbig)
    colors = ['#00FFA3' if row['Close'] >= row['Open'] else '#FF4B4B' for _, row in df.iterrows()]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'], name="Volumen",
        marker_color=colors, opacity=0.7
    ), row=2, col=1)

    # Layout Anpassung
    fig.update_layout(
        height=650,
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Achsen-Styling
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)', rangebreaks=[dict(bounds=["sat", "mon"])]) # Wochenenden ausblenden

    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Daten konnten nicht geladen werden. Bitte Ticker prüfen.")

# --- 6. TOP CHANCEN TABELLE ---
st.divider()
st.subheader("🚀 Top Markt-Chancen (Vola-Analyse)")
t_col1, t_col2 = st.columns(2)

# Hier würde man alle STOCKS_ONLY loopen und sortieren (vereinfacht für Demo)
top_data = []
for t in STOCKS_ONLY[:5]: # Beispielhaft für die ersten 5
    d = get_analysis(t)
    top_data.append({"Aktie": TICKER_NAMES[t], "Kurs": d["cp"], "Vol-Rel": d["vol_rel"], "Chance": d["chance"]})

df_top = pd.DataFrame(top_data).sort_values(by="Chance", ascending=False)
st.table(df_top)
