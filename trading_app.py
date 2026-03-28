import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. DESIGN & FARBLOGIK (BLAU-GRAU-GRÜN) ---
st.set_page_config(page_title="Trading-Terminal 2026", layout="wide")

st.markdown("""
    <style>
    /* Haupt-Hintergrund: Midnight Blue */
    .stApp { background-color: #001f3f; color: #ffffff; } 
    
    /* Metriken & Boxen: Dunkleres Blau mit blauem Rand */
    [data-testid="stMetric"], .heatmap-card {
        background-color: #002b55; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #0074D9;
    }
    
    /* Labels & Beschreibungen: Silbergrau (Lesbarkeit) */
    [data-testid="stMetricLabel"], .label-gray {
        color: #b0c4de !important; 
        font-size: 0.9rem !important;
        font-weight: 500;
    }
    
    /* Hauptwerte & Zahlen: Reinweiß */
    [data-testid="stMetricValue"], .value-white {
        color: #ffffff !important;
        font-weight: bold;
    }

    /* Tabellen-Fix: Weißer Text auf Blau */
    div[data-testid="stTable"] { background-color: #002b55 !important; border-radius: 10px; }
    .stTable td, .stTable th { 
        color: #ffffff !important; 
        background-color: #002b55 !important; 
        border-bottom: 1px solid #0074D9 !important;
    }
    
    /* Button: Kräftiges Blau */
    .stButton>button {
        background-color: #0074D9;
        color: white;
        border-radius: 5px;
        font-weight: bold;
        border: none;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Zeitstempel (Silbergrau/Cyan)
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: #00d4ff; font-size: 0.8rem;'>Letztes Update: {last_update}</p>", unsafe_allow_html=True)

# --- 2. ANALYSE-LOGIK ---
def get_analysis(ticker_dict, timeframe, is_fx=False, kontostand=25000, risiko=500):
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
            
            vol = hist['High'].rolling(14).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.003
            
            # 100% Kapital-Sicherung
            min_dist = (risiko * cp) / kontostand
            final_dist = max(sl_dist, min_dist)
            
            sl = cp - final_dist if is_bullish else cp + final_dist
            tp = cp + (final_dist * 2.5) if is_bullish else cp - (final_dist * 2.5)
            
            prob = 75 if is_bullish else 45
            lots = round(risiko / (abs(cp-sl) * 10000), 4) if is_fx else int(risiko / abs(cp-sl))
            kap_pct = ((lots * 100000 * cp if is_fx else lots * cp) / kontostand) * 100

            data_list.append({
                "Name": name, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{prob}%", "Kurs": cp, "Change": chg_pct,
                "Kapitaleinsatz": f"{min(kap_pct, 100.0):.2f}%",
                "SL": sl, "TP": tp, "Hist": hist
            })
        except: continue
    return data_list

# --- 3. SIDEBAR ---
st.sidebar.header("🛡️ Risikomanagement")
konto = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000)
risiko = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)

# --- 4. INDEX-HEATMAP (Logik: Grün bei Plus, Rot bei Minus) ---
st.subheader("🌍 Index-Heatmap (24h Change)")
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX", "^NSEI": "NIFTY", "XU100.IS": "BIST 100"}
idx_data = get_analysis(indices, "1d", False, konto, risiko)

if idx_data:
    cols = st.columns(len(idx_data))
    for i, item in enumerate(idx_data):
        # Grün-Logik für Gewinne, Dunkelrot für Verluste
        bg_color = "#008000" if item['Change'] >= 0 else "#800000"
        with cols[i]:
            st.markdown(f"""
                <div style="background-color: {bg_color}; border: 1px solid #0074D9; border-radius: 10px; padding: 15px; text-align: center; min-height: 100px;">
                    <span style="color: #b0c4de; font-size: 0.85rem; display: block; margin-bottom: 5px;">{item['Name']}</span>
                    <span style="color: #ffffff; font-size: 1.2rem; font-weight: bold;">{item['Change']:.2f}%</span>
                </div>
            """, unsafe_allow_html=True)

st.divider()

# --- 5. EUR/USD VISUALISIERUNG (WERT LINKS, PROZENT RECHTS) ---
st.subheader("💱 EUR/USD: Live-Kurs & Prozent")
fx_res = get_analysis({"EURUSD=X": "EUR/USD"}, intervall, True, konto, risiko)

if fx_res:
    res = fx_res[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Kurs", f"{res['Kurs']:.5f}")
    c2.metric("Wahrscheinlichkeit", res['Wahrscheinlichkeit'])
    c3.metric("Kapitaleinsatz", res['Kapitaleinsatz'])

    # Dual Axis Chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Candlestick(x=res['Hist'].index, open=res['Hist']['Open'], high=res['Hist']['High'],
                    low=res['Hist']['Low'], close=res['Hist']['Close'], name="Kurs"), secondary_y=False)
    
    # Prozent-Skala (Rechts)
    pct_trace = ((res['Hist']['Close'] / res['Kurs']) - 1) * 100
    fig.add_trace(go.Scatter(x=res['Hist'].index, y=pct_trace, line=dict(color='rgba(0,0,0,0)'), showlegend=False), secondary_y=True)

    # Trading-Linien (Grün/Rot/Blau)
    fig.add_hline(y=res['TP'], line_dash="dash", line_color="#00ff00", annotation_text=f"Ziel {res['TP']:.5f}", secondary_y=False)
    fig.add_hline(y=res['SL'], line_dash="dash", line_color="#ff4b4b", annotation_text=f"Stopp {res['SL']:.5f}", secondary_y=False)
    fig.add_hline(y=res['Kurs'], line_color="#00d4ff", annotation_text="Einstieg", secondary_y=False)
    
    fig.update_yaxes(title_text="<b>Kurs-Wert</b>", secondary_y=False, autorange=True)
    fig.update_yaxes(title_text="<b>Abweichung %</b>", secondary_y=True, showgrid=False)
    fig.update_layout(height=450, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 6. AKTIEN SCAN ---
if st.button("🚀 Markt-Scan starten"):
    stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall", "TSLA": "Tesla"}
    stock_res = get_analysis(stocks, intervall, False, konto, risiko)
    if stock_res:
        df = pd.DataFrame(stock_res)
        st.table(df[["Name", "Typ", "Wahrscheinlichkeit", "Kapitaleinsatz", "Kurs"]])

st.caption("Logik: Midnight Blue Hintergrund | Silbergrau für Labels | Grün/Rot für Performance.")
