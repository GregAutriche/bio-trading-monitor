import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DESIGN & STYLE (DUNKELBLAU) ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #001f3f; color: #ffffff; } /* Dunkelblaues Design */
    .stMetric { background-color: #003366; padding: 15px; border-radius: 10px; border: 1px solid #0074D9; }
    div[data-testid="stExpander"] { background-color: #002b55; border: none; }
    .stButton>button { background-color: #0074D9; color: white; border-radius: 5px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# Zeitstempel
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: #0074D9;'>Letztes Update: {last_update}</p>", unsafe_allow_html=True)

st.title("🚀 Trading-Monitor: Kapital-Check & Strategie")

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
    wetter_bonus = 5 # Sentiment-Faktor
    
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            # WAHRSCHEINLICHKEIT (Trend + RSI + Sentiment)
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            prob = 50 + (20 if is_bullish else 10) + wetter_bonus
            if (is_bullish and 50 < rsi < 70) or (not is_bullish and 30 < rsi < 50): prob += 20
            
            # SL / TP
            vol = hist['High'].rolling(10).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.02
            sl = cp - sl_dist if is_bullish else cp + sl_dist
            tp = cp + (sl_dist * 2.5) if is_bullish else cp - (sl_dist * 2.5)
            
            # KAPITAL-LOGIK (Statt Lots nun in % vom Kapital)
            risk_unit = abs(cp - sl)
            if is_fx:
                lots = round(risiko_eur / (risk_unit * 10000), 2)
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
                "SL": sl, "TP": tp, "Hist": hist, "Symbol": symbol
            })
        except: continue
    return data_list

# --- 4. EUR/USD VISUALISIERUNG ---
st.subheader("💱 EUR/USD Kapitaleinsatz & Chart")
fx_data = get_analysis({"EURUSD=X": "EUR/USD"}, intervall, is_fx=True)

if fx_data:
    res = fx_data[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live-Kurs", f"{res['Kurs']:.5f}")
    c2.metric("Wahrscheinlichkeit", res['Wahrscheinlichkeit'])
    c3.metric("Kapitaleinsatz", res['Kapitaleinsatz %'])
    c4.info(f"**Aktion:** {res['Typ']} | SL: {res['SL']:.5f}")

    fig = go.Figure(data=[go.Candlestick(x=res['Hist'].index, open=res['Hist']['Open'], 
                    high=res['Hist']['High'], low=res['Hist']['Low'], close=res['Hist']['Close'], name="EUR/USD")])
    fig.add_hline(y=res['TP'], line_dash="dash", line_color="#00ff00", annotation_text="Ziel")
    fig.add_hline(y=res['SL'], line_dash="dash", line_color="#ff0000", annotation_text="Stopp")
    fig.update_layout(height=350, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 5. INDIZES & AKTIEN ---
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX 50", "XU100.IS": "BIST 100"}
stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "RHM.DE": "Rheinmetall", "NVDA": "Nvidia", "TSLA": "Tesla", "AAPL": "Apple"}

st.subheader("📊 Indizes Übersicht")
idx_results = get_analysis(indices, intervall)
if idx_results:
    st.table(pd.DataFrame(idx_results)[["Name", "Kurs", "Wahrscheinlichkeit", "Kapitaleinsatz %"]])

if st.button("🚀 Markt-Scan starten"):
    all_stocks = get_analysis(stocks, intervall)
    if all_stocks:
        df = pd.DataFrame(all_stocks)
        l, r = st.columns(2)
        with l:
            st.success(f"🔥 Top {top_n} CALLS")
            st.table(df[df['Typ'] == "CALL 🟢"].sort_values("Prob_Val", ascending=False).head(top_n)[["Name", "Wahrscheinlichkeit", "Kapitaleinsatz %", "Ziel %"]])
        with r:
            st.error(f"📉 Top {top_n} PUTS")
            st.table(df[df['Typ'] == "PUT 🔴"].sort_values("Prob_Val", ascending=False).head(top_n)[["Name", "Wahrscheinlichkeit", "Kapitaleinsatz %", "Ziel %"]])

st.caption("Alle Berechnungen basieren auf einem fixen Risiko von 500€ pro Trade. Der Kapitaleinsatz zeigt, wie viel vom Gesamtkonto für diesen Trade bewegt wird.")
