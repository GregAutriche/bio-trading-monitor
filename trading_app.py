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
    [data-testid="stMetric"] { background-color: #002b55; padding: 20px; border-radius: 12px; border: 1px solid #0074D9; }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    div[data-testid="stTable"] { background-color: #002b55 !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #ffffff !important; background-color: #002b55 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.sidebar.header("🛡️ Risikomanagement")
konto = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000)
risiko = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall wählen", ["1d", "1h", "15m", "5m"], index=0)

col_h1, col_h2 = st.columns(2)
with col_h1:
    st.markdown(f"### 🕒 Letztes Update: <span style='color:#00d4ff;'>{last_update}</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<h3 style='text-align:right;'>Basis: <span style='color:#00d4ff;'>{intervall}</span></h3>", unsafe_allow_html=True)

# --- 3. ANALYSE-LOGIK ---
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
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            weather = "☀️" if is_bullish and chg_pct > 0.2 else "☁️" if is_bullish else "⛈️"
            
            # SL-Berechnung (Volatilitätsbasiert)
            vol = hist['High'].rolling(14).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.005
            
            # 100% Kapital-Sicherung: Verhindert extreme Skalierung wie im Bild
            min_sl_dist = (risiko_val * cp) / kontostand if not is_fx else (risiko_val * cp) / (kontostand / 50)
            final_dist = max(sl_dist, min_sl_dist)
            
            sl = cp - final_dist if is_bullish else cp + final_dist
            tp = cp + (final_dist * 2.5) if is_bullish else cp - (final_dist * 2.5)
            
            data_list.append({
                "Name": name, "Symbol": symbol, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Chance": f"{75 if is_bullish else 45}%", "Kurs": cp, "Change": chg_pct,
                "Kapitaleinsatz": f"{min(((risiko_val/abs(cp-sl))*cp/kontostand)*100, 100.0):.2f}%",
                "SL": sl, "TP": tp, "Hist": hist, "is_fx": is_fx, "Wetter": weather
            })
        except: continue
    return data_list

# --- 4. GRAFIK-FUNKTION (DUAL AXIS MIT FIXIERTER SKALIERUNG) ---
def plot_dual_axis_candlesticks(item):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Echte Candlesticks auf linker Achse
    fig.add_trace(go.Candlestick(
        x=item['Hist'].index, open=item['Hist']['Open'], high=item['Hist']['High'],
        low=item['Hist']['Low'], close=item['Hist']['Close'], name="Kurs"
    ), secondary_y=False)
    
    # Prozent-Skala Rechts (Relativ zum aktuellen Kurs)
    current_price = item['Kurs']
    pct_trace = ((item['Hist']['Close'] / current_price) - 1) * 100
    fig.add_trace(go.Scatter(x=item['Hist'].index, y=pct_trace, line=dict(color='rgba(0,0,0,0)'), showlegend=False), secondary_y=True)
    
    # Trading-Linien
    dec = 5 if item['is_fx'] else 2
    fig.add_hline(y=item['TP'], line_dash="dash", line_color="#00ff00", annotation_text=f"Ziel {item['TP']:.{dec}f}")
    fig.add_hline(y=item['SL'], line_dash="dash", line_color="#ff4b4b", annotation_text=f"Stopp {item['SL']:.{dec}f}")
    fig.add_hline(y=current_price, line_color="#00d4ff", annotation_text="Entry")

    # WICHTIG: Autorange fixiert die Kerzen in der Mitte
    fig.update_yaxes(title_text="<b>Kurs-Wert (Links)</b>", secondary_y=False, autorange=True, fixedrange=False)
    fig.update_yaxes(title_text="<b>Abweichung % (Rechts)</b>", secondary_y=True, showgrid=False)
    
    fig.update_layout(height=500, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# --- 5. EUR/USD SEKTION ---
st.subheader("💱 EUR/USD Live-Analyse")
fx_res = get_analysis({"EURUSD=X": "EUR/USD"}, intervall, True, konto, risiko)
if fx_res:
    res = fx_res[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Kurs", f"{res['Kurs']:.5f}", f"{res['Wetter']} Stimmung")
    c2.metric("Chance", res['Chance'])
    c3.metric("Richtung", res['Typ'].split(" ")[0])
    plot_dual_axis_candlesticks(res)

st.divider()

# --- 6. TOP 5 AKTIEN ---
st.subheader("🔥 Top 5 Aktien-Chancen")
stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall", "TSLA": "Tesla", "AAPL": "Apple"}
all_results = get_analysis(stocks, intervall, False, konto, risiko)

if all_results:
    df = pd.DataFrame(all_results)
    l, r = st.columns(2)
    with l:
        st.success("Top 5 CALL (Long)")
        st.table(df[df['Typ'] == "CALL 🟢"].head(5)[["Name", "Chance", "Wetter", "Kurs"]])
    with r:
        st.error("Top 5 PUT (Short)")
        st.table(df[df['Typ'] == "PUT 🔴"].head(5)[["Name", "Chance", "Wetter", "Kurs"]])

    st.subheader("🔍 Aktien Detail-Ansicht")
    selection = st.selectbox("Aktie wählen:", df['Name'].tolist())
    if selection:
        sel_item = next(x for x in all_results if x['Name'] == selection)
        plot_dual_axis_candlesticks(sel_item)
