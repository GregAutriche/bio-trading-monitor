import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. DESIGN & FARBLOGIK (MIDNIGHT BLUE) ---
st.set_page_config(page_title="Trading-Terminal 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: #ffffff; } 
    div[data-testid="stTable"] { background-color: #002b55 !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #ffffff !important; background-color: #002b55 !important; border-bottom: 1px solid #0074D9 !important; }
    [data-testid="stMetric"] { background-color: #002b55; border: 1px solid #0074D9; border-radius: 10px; }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; font-size: 0.9rem !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: bold; }
    .stButton>button { background-color: #0074D9; color: white; font-weight: bold; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR PARAMETER ---
st.sidebar.header("🛡️ Risikomanagement")
konto = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000)
risiko = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall wählen", ["1d", "1h", "15m", "5m"], index=0)

# --- 3. HEADER: UPDATE & BASIS ---
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
col_h1, col_h2 = st.columns(2)
with col_h1:
    st.markdown(f"### 🕒 Letztes Update: <span style='color:#00d4ff;'>{last_update}</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<h3 style='text-align:right;'>Basis: <span style='color:#00d4ff;'>{intervall}</span></h3>", unsafe_allow_html=True)

# --- 4. ANALYSE-LOGIK MIT VOLUMEN-TREND ---
def get_analysis(ticker_dict, timeframe, is_fx=False, kontostand=25000, risiko_val=500):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if hist.empty or len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            chg_pct = ((cp / prev_close) - 1) * 100
            
            # Volumen-Logik: Aktuelles vs. Durchschnitt (20 Perioden)
            current_vol = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].tail(20).mean()
            vol_trend_pct = ((current_vol / avg_vol) - 1) * 100 if avg_vol > 0 else 0
            
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            # SL/TP & 100% Sicherung
            vol_std = hist['High'].rolling(14).std().iloc[-1]
            sl_dist_raw = vol_std * 2 if vol_std > 0 else cp * 0.005
            min_sl_dist = (risiko_val * cp) / kontostand if not is_fx else (risiko_val * cp) / (kontostand / 100)
            final_dist = max(sl_dist_raw, min_sl_dist)
            
            sl = cp - final_dist if is_bullish else cp + final_dist
            tp = cp + (final_dist * 2.5) if is_bullish else cp - (final_dist * 2.5)
            
            data_list.append({
                "Name": name, "Symbol": symbol, "Typ": "CALL" if is_bullish else "PUT",
                "Chance": f"{75 if is_bullish else 45}%", "Kurs": cp, "Change": chg_pct,
                "Volumen": current_vol, "Vol_Trend": vol_trend_pct,
                "SL": sl, "TP": tp, "CRV": round(abs(tp-cp)/abs(cp-sl), 1),
                "Hist": hist, "is_fx": is_fx, "Wetter": "☀️" if is_bullish else "⛈️"
            })
        except: continue
    return data_list

# --- 5. GRAFIK-FUNKTION (DUAL AXIS & VOLUMEN-BALKEN) ---
def plot_advanced_chart(item):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                        row_width=[0.2, 0.8], specs=[[{"secondary_y": True}], [{"secondary_y": False}]])
    
    # 1. Candlesticks (Links)
    fig.add_trace(go.Candlestick(x=item['Hist'].index, open=item['Hist']['Open'], high=item['Hist']['High'],
                    low=item['Hist']['Low'], close=item['Hist']['Close'], name="Kurs"), row=1, col=1, secondary_y=False)
    
    # 2. Prozent-Skala (Rechts)
    pct_trace = ((item['Hist']['Close'] / item['Kurs']) - 1) * 100
    fig.add_trace(go.Scatter(x=item['Hist'].index, y=pct_trace, line=dict(color='rgba(0,0,0,0)'), showlegend=False), row=1, col=1, secondary_y=True)
    
    # 3. Volumen-Balken (Unten)
    v_colors = ['#00ff00' if r['Open'] < r['Close'] else '#ff4b4b' for _, r in item['Hist'].iterrows()]
    fig.add_trace(go.Bar(x=item['Hist'].index, y=item['Hist']['Volume'], marker_color=v_colors, opacity=0.4), row=2, col=1)

    dec = 5 if item['is_fx'] else 2
    fig.add_hline(y=item['TP'], line_dash="dash", line_color="#00ff00", row=1, col=1)
    fig.add_hline(y=item['SL'], line_dash="dash", line_color="#ff4b4b", row=1, col=1)
    fig.add_hline(y=item['Kurs'], line_color="#00d4ff", row=1, col=1)

    fig.update_yaxes(title_text="Kurs", secondary_y=False, autorange=True, row=1, col=1)
    fig.update_yaxes(title_text="Veränderung %", secondary_y=True, showgrid=False, row=1, col=1)
    fig.update_layout(height=500, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# --- 6. INDEX-HEATMAP ---
st.subheader("🌍 Index-Heatmap")
indices_r1 = {"^GDAXI": "DAX", "^IXIC": "NASDAQ"}
indices_r2 = {"^STOXX50E": "EURO STOXX", "^NSEI": "NIFTY", "XU100.IS": "BIST 100"}

def render_row(ticker_dict):
    data = get_analysis(ticker_dict, "1d", False, konto, risiko)
    if data:
        cols = st.columns(len(ticker_dict))
        for i, item in enumerate(data):
            bg_color = "#008000" if item['Change'] >= 0 else "#800000"
            with cols[i]:
                st.markdown(f"""<div style="background-color:{bg_color};border:1px solid #0074D9;border-radius:10px;padding:12px;text-align:center;margin-bottom:10px;">
                    <span style="color:#b0c4de;font-size:0.8rem;display:block;">{item['Name']}</span>
                    <span style="color:#ffffff;font-size:1.1rem;font-weight:bold;display:block;">{item['Kurs']:,.0f}</span>
                    <span style="color:#ffffff;font-size:0.8rem;">{item['Change']:.2f}%</span></div>""", unsafe_allow_html=True)

render_row(indices_r1)
render_row(indices_r2)
st.divider()

# --- 7. EUR/USD LIVE-ANALYSE (REPARIERT) ---
st.subheader("💱 EUR/USD Live-Analyse")
fx_res_list = get_analysis({"EURUSD=X": "EUR/USD"}, intervall, True, konto, risiko)

if fx_res_list:
    # FEHLERBEHEBUNG: Wir nehmen das erste Element der Liste [0]
    res = fx_res_list[0] 
    
    # Jetzt kann die Grafik korrekt gezeichnet werden
    plot_advanced_chart(res)
    
    # Metriken UNTER dem Chart
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Kurs", f"{res['Kurs']:.5f}")
    m2.metric("Chance", res['Chance'])
    m3.metric("Richtung", res['Typ'])
    m4.metric("CRV", f"({res['CRV']})")


st.divider()

# --- 8. AKTIEN-SCANNER & DETAIL ---
st.subheader("🔍 Aktien Detail-Analyse")
stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall", "TSLA": "Tesla", "AAPL": "Apple"}
all_stock_results = get_analysis(stocks, intervall, False, konto, risiko)

if all_stock_results:
    df = pd.DataFrame(all_stock_results)
    selection = st.selectbox("Aktie wählen:", df['Name'].tolist())
    if selection:
        sel_item = next(x for x in all_stock_results if x['Name'] == selection)
        plot_advanced_chart(sel_item)
        
        # Metriken UNTER Chart (Anordnung wie im Bild)
        v1, v2, v3, v4 = st.columns(4)
        v1.metric("Kurs", f"{sel_item['Kurs']:.2f}")
        
        # Volumen-Logik mit Trend-Anzeige
        vol_color = "inverse" if sel_item['Vol_Trend'] > 15 and sel_item['Typ'] == "PUT" else "normal"
        v2.metric("Handelsvolumen", f"{sel_item['Volumen']:,.0f}", f"{sel_item['Vol_Trend']:+.1f}% vs Ø", delta_color=vol_color)
        
        v3.metric("Richtung", sel_item['Typ'])
        v4.metric("CRV", f"({sel_item['CRV']})")
        
        if sel_item['Vol_Trend'] > 25 and sel_item['Typ'] == "PUT":
            st.warning(f"⚠️ ACHTUNG: Extrem hohes Volumen ({sel_item['Vol_Trend']:.1f}% über Ø) bei Abwärtstrend – Möglicher Panik-Ausverkauf!")
