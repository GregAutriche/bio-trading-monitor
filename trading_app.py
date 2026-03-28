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
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    .stButton>button { background-color: #0074D9; color: white; font-weight: bold; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR ---
st.sidebar.header("🛡️ Risikomanagement")
konto = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000, step=1000)
risiko = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500, step=50)
intervall = st.sidebar.selectbox("Intervall wählen", ["1d", "1h", "15m", "5m"], index=0)

# --- 3. HEADER: UPDATE & BASIS ---
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
col_h1, col_h2 = st.columns(2)
with col_h1:
    st.markdown(f"### 🕒 Letztes Update: <span style='color:#00d4ff;'>{last_update}</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<h3 style='text-align:right;'>Basis: <span style='color:#00d4ff;'>{intervall}</span></h3>", unsafe_allow_html=True)

# --- 4. KORRIGIERTE ANALYSE-LOGIK ---
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
            
            # Wetter-Logik
            weather = "☀️" if is_bullish and chg_pct > 0.2 else "☁️" if is_bullish else "⛈️"
            
            # KORREKTUR LINKE LOGIK: SL-Distanz darf niemals größer als das Kapitalverhältnis sein
            # Max Distanz für 100% Kapital-Einsatz bei risiko_val Verlust
            max_allowed_dist = (risiko_val / kontostand) * cp
            
            # Volatilitäts-basierter SL (ATR-Annäherung)
            vol = hist['High'].rolling(14).max().iloc[-1] - hist['Low'].rolling(14).min().iloc[-1]
            sl_dist_raw = (vol / 5) # Ein Fünftel der Range als SL
            
            # Sicherstellen, dass SL-Distanz realistisch bleibt (zwischen 0.5% und max_allowed_dist)
            final_dist = max(cp * 0.005, min(sl_dist_raw, max_allowed_dist))
            
            sl = cp - final_dist if is_bullish else cp + final_dist
            tp = cp + (final_dist * 2.5) if is_bullish else cp - (final_dist * 2.5)
            
            risk_unit = abs(cp - sl)
            lots = round(risiko_val / (risk_unit * 10000), 4) if is_fx else int(risiko_val / risk_unit)
            kap_pct = ((lots * 100000 * cp if is_fx else lots * cp) / kontostand) * 100

            data_list.append({
                "Name": name, "Symbol": symbol, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Chance": f"{75 if is_bullish else 45}%", "Kurs": cp, "Change": chg_pct,
                "Kapitaleinsatz": f"{min(kap_pct, 100.0):.2f}%", "SL": sl, "TP": tp, 
                "Hist": hist, "is_fx": is_fx, "Wetter": weather
            })
        except: continue
    return data_list

# --- 5. INDEX-HEATMAP ---
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX", "^NSEI": "NIFTY", "XU100.IS": "BIST 100"}
idx_data = get_analysis(indices, "1d", False, konto, risiko)

if idx_data:
    cols = st.columns(len(idx_data))
    for i, item in enumerate(idx_data):
        bg_color = "#008000" if item['Change'] >= 0 else "#800000"
        with cols[i]:
            st.markdown(f"""<div style="background-color:{bg_color};border:1px solid #0074D9;border-radius:10px;padding:12px;text-align:center;">
                <span style="color:#b0c4de;font-size:0.8rem;display:block;">{item['Name']}</span>
                <span style="color:#ffffff;font-size:1.1rem;font-weight:bold;display:block;">{item['Kurs']:,.0f}</span>
                <span style="color:#ffffff;font-size:0.9rem;">{item['Change']:.2f}%</span></div>""", unsafe_allow_html=True)

st.divider()

# --- 6. GRAFIK-FUNKTION (DUAL AXIS: WERT LINKS / PROZENT RECHTS) ---
def plot_dual_axis_chart(item):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Candlesticks auf linker Achse (Primär)
    fig.add_trace(go.Candlestick(
        x=item['Hist'].index, open=item['Hist']['Open'], high=item['Hist']['High'],
        low=item['Hist']['Low'], close=item['Hist']['Close'], name="Kurs"
    ), secondary_y=False)
    
    # Prozent-Skala auf rechter Achse (Sekundär)
    current_price = item['Kurs']
    # Dummy-Trace für die Prozent-Skala
    fig.add_trace(go.Scatter(
        x=item['Hist'].index, 
        y=[((y / current_price) - 1) * 100 for y in item['Hist']['Close']],
        mode='lines', line=dict(color='rgba(0,0,0,0)'), showlegend=False
    ), secondary_y=True)

    # Trading-Linien (Immer auf linke Achse bezogen)
    dec = 5 if item['is_fx'] else 2
    fig.add_hline(y=item['TP'], line_dash="dash", line_color="#00ff00", annotation_text=f"Ziel {item['TP']:.{dec}f}", secondary_y=False)
    fig.add_hline(y=item['SL'], line_dash="dash", line_color="#ff4b4b", annotation_text=f"Stopp {item['SL']:.{dec}f}", secondary_y=False)
    fig.add_hline(y=current_price, line_color="#00d4ff", annotation_text=f"Entry {current_price:.{dec}f}", secondary_y=False)

    # Achsen-Beschriftungen
    fig.update_yaxes(title_text="<b>Kurs-Wert (Links)</b>", secondary_y=False, autorange=True)
    fig.update_yaxes(title_text="<b>Abweichung % (Rechts)</b>", secondary_y=True, showgrid=False)
    
    fig.update_layout(
        height=500, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f",
        margin=dict(l=0,r=0,t=20,b=0), xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 7. EUR/USD ANALYSE ---
st.subheader("💱 EUR/USD Live-Analyse")
fx_results = get_analysis({"EURUSD=X": "EUR/USD"}, intervall, True, konto, risiko)
if fx_results:
    res = fx_results[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Kurs", f"{res['Kurs']:.5f}", f"{res['Wetter']} Stimmung")
    c2.metric("Chance", res['Chance'])
    c3.metric("Richtung", res['Typ'].split(" ")[0])
    plot_dual_axis_chart(res)

st.divider()

# --- 8. TOP 5 AKTIEN ---
st.subheader("🔥 Top 5 Aktien-Chancen")
stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall", "TSLA": "Tesla", "AAPL": "Apple"}
stock_results = get_analysis(stocks, intervall, False, konto, risiko)

if stock_results:
    df = pd.DataFrame(stock_results)
    l, r = st.columns(2)
    with l:
        st.success("Top 5 CALL (Long)")
        st.table(df[df['Typ'] == "CALL 🟢"].sort_values("Chance", ascending=False).head(5)[["Name", "Chance", "Wetter", "Kurs"]])
    with r:
        st.error("Top 5 PUT (Short)")
        st.table(df[df['Typ'] == "PUT 🔴"].sort_values("Chance", ascending=False).head(5)[["Name", "Chance", "Wetter", "Kurs"]])

    st.subheader("🔍 Aktien Detail-Ansicht")
    selection = st.selectbox("Aktie wählen:", df['Name'].tolist())
    if selection:
        sel_item = next(x for x in stock_results if x['Name'] == selection)
        plot_dual_axis_chart(sel_item)
