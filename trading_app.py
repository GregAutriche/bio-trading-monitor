import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. DESIGN & STYLING ---
st.set_page_config(page_title="Trading-Terminal 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: #ffffff; } 
    [data-testid="stMetric"] { background-color: #002b55; padding: 15px; border-radius: 10px; border: 1px solid #0074D9; }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; font-size: 0.9rem !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR ---
st.sidebar.header("🛡️ Risikomanagement")
konto = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000)
risiko = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)

# --- 3. ANALYSE-LOGIK MIT VOLUMEN-TREND ---
def get_analysis_pro(ticker_dict, timeframe, kontostand=25000, risiko_val=500):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if hist.empty or len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            # Volumen-Logik
            current_vol = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].tail(20).mean()
            vol_change_pct = ((current_vol / avg_vol) - 1) * 100
            
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            # SL/TP Logik
            vol_std = hist['High'].rolling(14).std().iloc[-1]
            sl_dist = max(vol_std * 2, cp * 0.005)
            sl = cp - sl_dist if is_bullish else cp + sl_dist
            tp = cp + (sl_dist * 2.5) if is_bullish else cp - (sl_dist * 2.5)
            
            data_list.append({
                "Name": name, "Kurs": cp, "Volumen": current_vol, 
                "Vol_Change": vol_change_pct, "Typ": "CALL" if is_bullish else "PUT",
                "CRV": round(abs(tp-cp)/abs(cp-sl), 1), "Hist": hist, "SL": sl, "TP": tp
            })
        except: continue
    return data_list

# --- 4. CHART FUNKTION ---
def plot_clean_chart(item):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                        row_width=[0.2, 0.8], specs=[[{"secondary_y": True}], [{"secondary_y": False}]])
    
    # Kurs (Links) & % (Rechts)
    fig.add_trace(go.Candlestick(x=item['Hist'].index, open=item['Hist']['Open'], high=item['Hist']['High'], 
                                 low=item['Hist']['Low'], close=item['Hist']['Close'], name="Kurs"), row=1, col=1)
    
    pct_trace = ((item['Hist']['Close'] / item['Kurs']) - 1) * 100
    fig.add_trace(go.Scatter(x=item['Hist'].index, y=pct_trace, line=dict(color='rgba(0,0,0,0)'), showlegend=False), row=1, col=1, secondary_y=True)
    
    # Volumen
    colors = ['#00ff00' if r['Open'] < r['Close'] else '#ff4b4b' for _, r in item['Hist'].iterrows()]
    fig.add_trace(go.Bar(x=item['Hist'].index, y=item['Hist']['Volume'], marker_color=colors, opacity=0.4), row=2, col=1)

    fig.add_hline(y=item['TP'], line_dash="dash", line_color="#00ff00", row=1, col=1)
    fig.add_hline(y=item['SL'], line_dash="dash", line_color="#ff4b4b", row=1, col=1)
    
    fig.update_layout(height=500, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    fig.update_yaxes(autorange=True, row=1, col=1)
    st.plotly_chart(fig, use_container_width=True)

# --- 5. DASHBOARD ---
st.subheader("🔍 Aktien Detail-Analyse")
stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall", "AAPL": "Apple", "TSLA": "Tesla"}
results = get_analysis_pro(stocks, intervall, konto, risiko)

if results:
    selection = st.selectbox("Aktie wählen:", [r['Name'] for r in results])
    item = next(x for x in results if x['Name'] == selection)
    
    # 1. Chart Oben
    plot_clean_chart(item)
    
    # 2. Metriken UNTER dem Chart (wie im Bild)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Kurs", f"{item['Kurs']:.2f}")
    
    # Volumen-Veränderungslogik Anzeige
    vol_color = "normal" if abs(item['Vol_Change']) < 10 else "inverse"
    m2.metric("Handelsvolumen", f"{item['Volumen']:,.0f}", 
              f"{item['Vol_Change']:+.1f}% vs Ø", delta_color=vol_color)
    
    m3.metric("Richtung", item['Typ'])
    m4.metric("CRV", f"({item['CRV']})")
