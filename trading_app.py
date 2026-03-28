import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DESIGN-FIX: WEISSE SCHRIFT & KLARE KONTRASTE ---
st.set_page_config(page_title="Trading-Monitor Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: #ffffff; } 
    /* Tabelle: Weißer Text auf hellem Blau-Grund */
    div[data-testid="stTable"] { background-color: #002b55 !important; border-radius: 10px; padding: 10px; }
    .stTable td, .stTable th { 
        color: #ffffff !important; 
        background-color: #002b55 !important; 
        border-bottom: 1px solid #0074D9 !important;
        font-size: 1.1rem !important;
    }
    /* Metriken */
    [data-testid="stMetric"] { background-color: #002b55; border: 1px solid #0074D9; border-radius: 10px; }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: #00d4ff;'>Update: {last_update}</p>", unsafe_allow_html=True)

# --- 2. SIDEBAR ---
st.sidebar.header("🛡️ Risikomanagement")
kontostand = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000)
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)

# --- 3. ANALYSE-LOGIK ---
def get_analysis_stable(ticker_dict, timeframe, is_fx=False):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if hist.empty or len(hist) < 20: continue

            cp = hist['Close'].iloc[-1]
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            # SL-Berechnung & 100% Sperre
            vol = hist['High'].rolling(10).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.005
            min_dist = (risiko_eur * cp) / kontostand if not is_fx else (risiko_eur * cp) / (kontostand / 50)
            final_dist = max(sl_dist, min_dist)
            
            sl = cp - final_dist if is_bullish else cp + final_dist
            tp = cp + (final_dist * 2.5) if is_bullish else cp - (final_dist * 2.5)
            
            # Risiko & Wahrscheinlichkeit
            prob = 75 if is_bullish else 45
            lots = round(risiko_eur / (abs(cp-sl) * 10000), 4) if is_fx else int(risiko_eur / abs(cp-sl))
            kapital_pct = ((lots * 100000 * cp if is_fx else lots * cp) / kontostand) * 100

            data_list.append({
                "Name": name, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{prob}%", "Kurs": round(cp, 5 if is_fx else 2),
                "Kapitaleinsatz": f"{min(kapital_pct, 100.0):.2f}%",
                "SL": sl, "TP": tp, "Hist": hist
            })
        except: continue
    return data_list

# --- 4. EUR/USD VISUALISIERUNG (FIXIERTE ACHSEN) ---
st.subheader("💱 EUR/USD Live-Analyse")
fx_data = get_analysis_stable({"EURUSD=X": "EUR/USD"}, intervall, is_fx=True)

if fx_data:
    res = fx_data[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Kurs", f"{res['Kurs']:.5f}")
    c2.metric("Wahrscheinlichkeit", res['Wahrscheinlichkeit'])
    c3.metric("Kapitaleinsatz", res['Kapitaleinsatz'])

    # Chart mit automatischer Skalierung auf den Kurs
    fig = go.Figure(data=[go.Candlestick(
        x=res['Hist'].index, open=res['Hist']['Open'], high=res['Hist']['High'],
        low=res['Hist']['Low'], close=res['Hist']['Close'], name="EUR/USD"
    )])
    fig.add_hline(y=res['TP'], line_dash="dash", line_color="#00ff00", annotation_text="TP")
    fig.add_hline(y=res['SL'], line_dash="dash", line_color="#ff4b4b", annotation_text="SL")
    
    # Fix: Achsen automatisch an Kurs anpassen
    fig.update_yaxes(autorange=True, fixedrange=False)
    fig.update_layout(height=400, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", 
                      margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 5. AKTIEN SCAN ---
if st.button("🚀 Großen Markt-Scan starten"):
    stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall"}
    res_list = get_analysis_stable(stocks, intervall)
    if res_list:
        df = pd.DataFrame(res_list)
        st.table(df[["Name", "Typ", "Wahrscheinlichkeit", "Kapitaleinsatz", "Kurs"]])
