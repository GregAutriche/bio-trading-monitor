import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DESIGN & STYLE (OPTIMIERTE LESBARKEIT) ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")

st.markdown("""
    <style>
    /* Haupt-Hintergrund */
    .stApp { background-color: #001f3f; color: #ffffff; } 
    
    /* Metriken (Karten) Optimierung */
    [data-testid="stMetric"] {
        background-color: #002b55; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #0074D9;
        color: #ffffff;
    }
    
    /* Lesbarkeit der Labels (kleine Schrift oben in der Karte) */
    [data-testid="stMetricLabel"] {
        color: #b0c4de !important; /* Helles Silbergrau */
        font-size: 1.1rem !important;
        font-weight: 500;
    }
    
    /* Lesbarkeit der Werte (große Zahl in der Karte) */
    [data-testid="stMetricValue"] {
        color: #ffffff !important; /* Reinweiß für maximalen Kontrast */
        font-weight: bold;
    }

    /* Tabellen-Styling */
    .stTable { background-color: #002b55; color: white; }
    
    /* Button Styling */
    .stButton>button {
        background-color: #0074D9;
        color: white;
        border-radius: 5px;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# Zeitstempel oben rechts
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: #00d4ff;'>Update: {last_update}</p>", unsafe_allow_html=True)

st.title("🚀 Trading-Monitor: Strategie 3-10 Tage")

# --- 2. SIDEBAR PARAMETER ---
st.sidebar.header("🛡️ Risikomanagement")
kontostand = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000, step=1000)
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
st.sidebar.markdown("---")
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)
top_n = st.sidebar.slider("Top-Signale anzeigen", 1, 10, 5)

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
            
            # RSI Berechnung
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            prob = 55 + (20 if is_bullish else 0)
            if (is_bullish and 45 < rsi < 70) or (not is_bullish and 30 < rsi < 55): prob += 20
            
            vol = hist['High'].rolling(10).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.02
            sl = cp - sl_dist if is_bullish else cp + sl_dist
            tp = cp + (sl_dist * 2.5) if is_bullish else cp - (sl_dist * 2.5)
            
            # Kapital-Einsatz Logik
            risk_unit = abs(cp - sl)
            if is_fx:
                lots = round(risiko_eur / (risk_unit * 10000), 4)
                pos_wert_eur = lots * 100000 * cp
            else:
                stueck = int(risiko_eur / risk_unit)
                pos_wert_eur = stueck * cp
            
            kapital_einsatz_pct = (pos_wert_eur / kontostand) * 100

            data_list.append({
                "Name": name, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{min(prob, 98)}%", "Prob_Val": prob,
                "Kurs": round(cp, 5 if is_fx else 2),
                "Kapitaleinsatz %": f"{kapital_einsatz_pct:.2f}%",
                "Ziel %": f"{abs((tp-cp)/cp)*100:.2f}%",
                "SL": round(sl, 5 if is_fx else 2), "TP": round(tp, 5 if is_fx else 2),
                "Hist": hist, "Symbol": symbol
            })
        except: continue
    return data_list

# --- 4. EUR/USD VISUALISIERUNG ---
st.subheader("💱 EUR/USD Live-Analyse")
fx_data_list = get_analysis({"EURUSD=X": "EUR/USD"}, intervall, is_fx=True)

if fx_data_list:
    res = fx_data_list[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kurs", f"{res['Kurs']:.5f}")
    c2.metric("Wahrscheinlichkeit", res['Wahrscheinlichkeit'])
    c3.metric("Kapitaleinsatz", res['Kapitaleinsatz %'])
    c4.info(f"**Aktion:** {res['Typ']} | **SL:** {res['SL']:.5f}")

    # Candlestick Chart
    fig = go.Figure(data=[go.Candlestick(x=res['Hist'].index, open=res['Hist']['Open'], 
                    high=res['Hist']['High'], low=res['Hist']['Low'], close=res['Hist']['Close'], name="EUR/USD")])
    fig.add_hline(y=res['TP'], line_dash="dash", line_color="#00ff00", annotation_text="Ziel")
    fig.add_hline(y=res['SL'], line_dash="dash", line_color="#ff4b4b", annotation_text="Stopp")
    fig.update_layout(height=350, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=10,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 5. INDIZES & AKTIEN-SCAN ---
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX 50", "XU100.IS": "BIST 100"}
stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "RHM.DE": "Rheinmetall", "NVDA": "Nvidia", "TSLA": "Tesla", "AAPL": "Apple", "MSFT": "Microsoft"}

st.subheader("📊 Indizes Übersicht")
idx_results = get_analysis(indices, intervall)
if idx_results:
    st.table(pd.DataFrame(idx_results)[["Name", "Kurs", "Wahrscheinlichkeit", "Kapitaleinsatz %", "Typ"]])

if st.button("🚀 Großen Markt-Scan starten"):
    all_stocks = get_analysis(stocks, intervall)
    if all_stocks:
        df = pd.DataFrame(all_stocks)
        l, r = st.columns(2)
        with l:
            st.success(f"🔥 Top {top_n} CALLS (Long)")
            calls = df[df['Typ'] == "CALL 🟢"].sort_values("Prob_Val", ascending=False).head(top_n)
            st.table(calls[["Name", "Wahrscheinlichkeit", "Kapitaleinsatz %", "Ziel %"]])
        with r:
            st.error(f"📉 Top {top_n} PUTS (Short)")
            puts = df[df['Typ'] == "PUT 🔴"].sort_values("Prob_Val", ascending=False).head(top_n)
            st.table(puts[["Name", "Wahrscheinlichkeit", "Kapitaleinsatz %", "Ziel %"]])

st.caption("Alle Werte sind nun durch hohen Kontrast (Weiß auf Dunkelblau) optimiert.")
