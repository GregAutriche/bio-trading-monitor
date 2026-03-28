import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DESIGN & FARBLOGIK ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: #ffffff; } 
    /* Tabellen-Hintergrund und Textfarbe fixieren */
    div[data-testid="stTable"] { background-color: #002b55 !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #ffffff !important; background-color: #002b55 !important; border-bottom: 1px solid #0074D9 !important; }
    /* Metriken */
    [data-testid="stMetric"] { background-color: #002b55; padding: 15px; border-radius: 10px; border: 1px solid #0074D9; }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    /* Buttons */
    .stButton>button { background-color: #0074D9; color: white; font-weight: bold; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: #00d4ff;'>Update: {last_update}</p>", unsafe_allow_html=True)
st.title("🚀 Trading-Monitor: Strategie 3-10 Tage")

# --- 2. SIDEBAR ---
st.sidebar.header("🛡️ Risikomanagement")
kontostand = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000, step=1000)
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)
top_n = st.sidebar.slider("Top-Signale", 1, 10, 5)

# --- 3. ANALYSE-LOGIK ---
def get_analysis(ticker_dict, timeframe, is_fx=False):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if len(hist) < 20: continue
            cp = hist['Close'].iloc[-1]
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            vol = hist['High'].rolling(10).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.02
            
            # 100% Kapital-Limit Logik
            min_sl_dist = (risiko_eur * cp) / kontostand if not is_fx else (risiko_eur * cp) / (kontostand / 100)
            final_sl_dist = max(sl_dist, min_sl_dist)
            sl = cp - final_sl_dist if is_bullish else cp + final_sl_dist
            tp = cp + (final_sl_dist * 2.5) if is_bullish else cp - (final_sl_dist * 2.5)

            risk_per_unit = abs(cp - sl)
            if is_fx:
                lots = round(risiko_eur / (risk_unit * 10000), 4) if risk_per_unit > 0 else 0
                pos_wert = lots * 100000 * cp
            else:
                stueck = int(risiko_eur / risk_per_unit) if risk_per_unit > 0 else 0
                pos_wert = stueck * cp
            
            kapital_pct = (pos_wert / kontostand) * 100
            prob = 60 + (15 if is_bullish else 0)

            data_list.append({
                "Name": name, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{prob}%", "Prob_Val": prob,
                "Kurs": round(cp, 5 if is_fx else 2),
                "Kapitaleinsatz": f"{min(kapital_pct, 100.0):.2f}%",
                "SL": sl, "TP": tp, "Hist": hist
            })
        except: continue
    return data_list

# --- 4. FOREX ---
st.subheader("💱 EUR/USD Live-Analyse")
fx_data = get_analysis({"EURUSD=X": "EUR/USD"}, intervall, is_fx=True)
if fx_data:
    res = fx_data[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Kurs", f"{res['Kurs']:.5f}")
    c2.metric("Wahrscheinlichkeit", res['Wahrscheinlichkeit'])
    c3.metric("Kapitaleinsatz", res['Kapitaleinsatz'])
    
    fig = go.Figure(data=[go.Candlestick(x=res['Hist'].index, open=res['Hist']['Open'], 
                    high=res['Hist']['High'], low=res['Hist']['Low'], close=res['Hist']['Close'], name="EUR/USD")])
    fig.update_layout(height=300, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 5. AKTIEN SCAN ---
if 'stock_results' not in st.session_state:
    st.session_state.stock_results = None

if st.button("🚀 Markt-Scan starten"):
    stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall", "TSLA": "Tesla"}
    st.session_state.stock_results = get_analysis(stocks, intervall)

# Hier wird der Fehler behoben: r wird jetzt sicher innerhalb der Spalten definiert
if st.session_state.stock_results:
    df = pd.DataFrame(st.session_state.stock_results)
    col_left, col_right = st.columns(2) # Eindeutige Namen für Spalten
    
    with col_left:
        st.success(f"🔥 Top {top_n} CALLS")
        calls = df[df['Typ'] == "CALL 🟢"].sort_values("Prob_Val", ascending=False).head(top_n)
        if not calls.empty:
            st.table(calls[["Name", "Wahrscheinlichkeit", "Kapitaleinsatz", "Kurs"]])
        else:
            st.write("Keine CALL Signale gefunden.")
            
    with col_right:
        st.error(f"📉 Top {top_n} PUTS")
        puts = df[df['Typ'] == "PUT 🔴"].sort_values("Prob_Val", ascending=False).head(top_n)
        if not puts.empty:
            st.table(puts[["Name", "Wahrscheinlichkeit", "Kapitaleinsatz", "Kurs"]])
        else:
            st.write("Keine PUT Signale gefunden.")
