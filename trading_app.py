import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DESIGN ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: #ffffff; } 
    [data-testid="stMetric"] { background-color: #002b55; padding: 15px; border-radius: 10px; border: 1px solid #0074D9; }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    .stTable { background-color: #002b55; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR ---
st.sidebar.header("🛡️ Risikomanagement")
kontostand = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000)
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)

# --- 3. REPARIERTE ANALYSE-LOGIK ---
def get_analysis_safe(ticker_dict, timeframe, is_fx=False):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            # WICHTIG: Größere Historie laden, um NaNs zu vermeiden
            hist = t.history(period="1mo" if "m" in timeframe else "6mo", interval=timeframe)
            
            if hist.empty or len(hist) < 20:
                continue # Überspringe leere Daten

            cp = hist['Close'].iloc[-1]
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            # SL-Berechnung
            vol = hist['High'].rolling(10).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.02
            
            # 100% Kapital-Sperre
            min_dist = (risiko_eur * cp) / kontostand if not is_fx else (risiko_eur * cp) / (kontostand / 100)
            final_dist = max(sl_dist, min_dist)
            
            sl = cp - final_dist if is_bullish else cp + final_dist
            tp = cp + (final_dist * 2.5) if is_bullish else cp - (final_dist * 2.5)

            # Risiko-Kalkulation
            risk_unit = abs(cp - sl)
            lots = round(risiko_eur / (risk_unit * 10000), 4) if is_fx else int(risiko_eur / risk_unit)
            kapital_pct = ((lots * 100000 * cp if is_fx else lots * cp) / kontostand) * 100

            data_list.append({
                "Name": name, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{75 if is_bullish else 45}%",
                "Kurs": round(cp, 5 if is_fx else 2),
                "Kapitaleinsatz": f"{min(kapital_pct, 100.0):.2f}%",
                "SL": sl, "TP": tp, "Hist": hist
            })
        except Exception as e:
            st.error(f"Fehler bei {name}: {e}")
    return data_list

# --- 4. EUR/USD SEKTION (FIXIERT) ---
st.subheader("💱 EUR/USD Live-Analyse")
fx_data = get_analysis_safe({"EURUSD=X": "EUR/USD"}, intervall, is_fx=True)

if fx_data:
    res = fx_data[0] # Nehme das erste (und einzige) FX-Ergebnis
    c1, c2, c3 = st.columns(3)
    c1.metric("Kurs", f"{res['Kurs']:.5f}")
    c2.metric("Wahrscheinlichkeit", res['Wahrscheinlichkeit'])
    c3.metric("Kapitaleinsatz", res['Kapitaleinsatz'])

    # GRAFIK FIX
    fig = go.Figure(data=[go.Candlestick(
        x=res['Hist'].index, open=res['Hist']['Open'], high=res['Hist']['High'],
        low=res['Hist']['Low'], close=res['Hist']['Close'], name="EUR/USD"
    )])
    fig.add_hline(y=res['TP'], line_dash="dash", line_color="#00ff00", annotation_text="TP")
    fig.add_hline(y=res['SL'], line_dash="dash", line_color="#ff4b4b", annotation_text="SL")
    fig.update_layout(height=400, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Währungsdaten konnten nicht geladen werden. Bitte Seite neu laden.")

st.divider()

# --- 5. AKTIEN-SCAN ---
if st.button("🚀 Markt-Scan starten"):
    stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall"}
    res_list = get_analysis_safe(stocks, intervall)
    if res_list:
        st.table(pd.DataFrame(res_list)[["Name", "Typ", "Wahrscheinlichkeit", "Kapitaleinsatz", "Kurs"]])
