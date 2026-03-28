import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. DESIGN & FARBLOGIK ---
st.set_page_config(page_title="Trading-Terminal 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: #ffffff; } 
    div[data-testid="stTable"] { background-color: #002b55 !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #ffffff !important; background-color: #002b55 !important; border-bottom: 1px solid #0074D9 !important; }
    [data-testid="stMetric"] { background-color: #002b55; border: 1px solid #0074D9; border-radius: 10px; }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; font-size: 0.9rem !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    .stButton>button { background-color: #0074D9; color: white; font-weight: bold; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ANALYSE-LOGIK ---
def get_analysis(ticker_dict, timeframe, is_fx=False, kontostand=25000, risiko=500):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if hist.empty or len(hist) < 20: continue
            cp = hist['Close'].iloc[-1]
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            vol = hist['High'].rolling(14).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.005
            min_dist = (risiko * cp) / kontostand
            final_dist = max(sl_dist, min_dist)
            sl = cp - final_dist if is_bullish else cp + final_dist
            tp = cp + (final_dist * 2.5) if is_bullish else cp - (final_dist * 2.5)
            prob = 75 if is_bullish else 45
            lots = round(risiko / (abs(cp-sl) * 10000), 4) if is_fx else int(risiko / abs(cp-sl))
            kap_pct = ((lots * 100000 * cp if is_fx else lots * cp) / kontostand) * 100
            data_list.append({
                "Name": name, "Symbol": symbol, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{prob}%", "Prob_Val": prob, "Kurs": cp,
                "Kapitaleinsatz": f"{min(kap_pct, 100.0):.2f}%", "SL": sl, "TP": tp, "Hist": hist
            })
        except: continue
    return data_list

# --- 3. SIDEBAR ---
st.sidebar.header("🛡️ Risikomanagement")
konto = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000)
risiko = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)

# --- 4. TOP 5 CHANCEN ---
st.subheader("🔥 Top 5 Trading-Chancen")
stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall", "TSLA": "Tesla", "AAPL": "Apple", "MSFT": "Microsoft"}
all_results = get_analysis(stocks, intervall, False, konto, risiko)

if all_results:
    df = pd.DataFrame(all_results)
    col_l, col_r = st.columns(2)
    with col_l:
        st.success("Top 5 CALL (Long)")
        calls = df[df['Typ'] == "CALL 🟢"].sort_values("Prob_Val", ascending=False).head(5)
        st.table(calls[["Name", "Wahrscheinlichkeit", "Kapitaleinsatz", "Kurs"]])
    with col_r:
        st.error("Top 5 PUT (Short)")
        puts = df[df['Typ'] == "PUT 🔴"].sort_values("Prob_Val", ascending=False).head(5)
        st.table(puts[["Name", "Wahrscheinlichkeit", "Kapitaleinsatz", "Kurs"]])

    st.divider()

    # --- 5. EINZEL-ANALYSE MIT GRAFIK ---
    st.subheader("🔍 Einzel-Analyse & Chart")
    selection = st.selectbox("Aktie zur Detail-Ansicht wählen:", df['Name'].tolist())
    
    if selection:
        item = next(x for x in all_results if x['Name'] == selection)
        c1, c2, c3 = st.columns(3)
        c1.metric("Kurs", f"{item['Kurs']:.2f}")
        c2.metric("Ziel (TP)", f"{item['TP']:.2f}")
        c3.metric("Stopp (SL)", f"{item['SL']:.2f}")

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Candlestick(x=item['Hist'].index, open=item['Hist']['Open'], high=item['Hist']['High'], low=item['Hist']['Low'], close=item['Hist']['Close'], name="Kurs"), secondary_y=False)
        fig.add_hline(y=item['TP'], line_dash="dash", line_color="#00ff00", annotation_text="Ziel (TP)")
        fig.add_hline(y=item['SL'], line_dash="dash", line_color="#ff4b4b", annotation_text="Stopp (SL)")
        fig.update_layout(height=450, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
