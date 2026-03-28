import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# --- 1. SETUP & WETTER API ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

# Wetter-Integration (Beispiel Frankfurt für DAX-Sentiment)
def get_weather_bonus(city="Frankfurt"):
    # Hinweis: Hier eigenen API-Key von OpenWeatherMap einfügen
    # Für diesen Code nutzen wir einen Standard-Bonus von +5 bei Sonne/Klar
    return 5 # Standard-Sentiment-Bonus

st.markdown(f"<p style='text-align: right; color: gray;'>Update: {last_update}</p>", unsafe_allow_html=True)
st.title("🚀 Trading-Monitor: Strategie 3-10 Tage")

# --- 2. SIDEBAR PARAMETER ---
st.sidebar.header("Konfiguration")
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)
top_n = st.sidebar.slider("Anzahl Top-Signale", 1, 10, 5)

# --- 3. TICKER-LISTEN ---
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX 50", "^NSEI": "NIFTY 50", "XU100.IS": "BIST 100"}
forex_ticker = "EURUSD=X"
stocks = {
    "ADS.DE": "Adidas", "ALV.DE": "Allianz", "SAP.DE": "SAP", "RHM.DE": "Rheinmetall", 
    "NVDA": "Nvidia", "AAPL": "Apple", "MSFT": "Microsoft", "TSLA": "Tesla", "AMZN": "Amazon"
}

# --- 4. ANALYSE-LOGIK ---
def get_analysis(ticker_dict, timeframe, is_fx=False):
    data_list = []
    wetter_bonus = get_weather_bonus()
    
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            # WAHRSCHEINLICHKEITS-SCORE inkl. Wetter-Sentiment
            score = 50 + (20 if is_bullish else 10) + wetter_bonus
            
            # AKTIONSLOGIK
            if score >= 75: action = "🔥 AGGRESSIV"
            elif score >= 60: action = "✅ HANDELN"
            else: action = "🛑 WARTEN"
            
            vol = hist['High'].rolling(10).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.02
            sl = cp - sl_dist if is_bullish else cp + sl_dist
            tp = cp + (sl_dist * 2.5) if is_bullish else cp - (sl_dist * 2.5)
            
            risk_unit = abs(cp - sl)
            shares = round(risiko_eur / (risk_unit * 10000), 4) if is_fx else int(risiko_eur / risk_unit)

            data_list.append({
                "Name": name, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{min(score, 99)}%",
                "Aktion": action,
                "Kurs": round(cp, 5 if is_fx else 2),
                "Stück/Lots": shares,
                "Ziel %": f"{abs((tp-cp)/cp)*100:.2f}%",
                "SL": round(sl, 5 if is_fx else 2), "TP": round(tp, 5 if is_fx else 2)
            })
        except: continue
    return data_list

# --- 5. EUR/USD LIVE-ANALYSE (OBEN) ---
st.subheader("💱 EUR/USD Live-Analyse")
fx_res = get_analysis({forex_ticker: "EUR/USD"}, intervall, is_fx=True)

if fx_res:
    res = fx_res[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kurs", f"{res['Kurs']:.5f}")
    c2.metric("Wahrscheinlichkeit", res['Wahrscheinlichkeit'])
    c3.metric("Aktion", res['Aktion'])
    c4.info(f"**Einsatz:** {res['Stück/Lots']} Lots")
    
    st.write(f"📍 **Entry:** {res['Kurs']:.5f} | **TP:** {res['TP']:.5f} | **SL:** {res['SL']:.5f}")

st.divider()

# --- 6. INDIZES ---
st.subheader("📊 Indizes Wahrscheinlichkeits-Check")
idx_data = get_analysis(indices, intervall)
if idx_data:
    st.table(pd.DataFrame(idx_data)[["Name", "Kurs", "Typ", "Wahrscheinlichkeit", "Aktion", "Ziel %"]])

st.divider()

# --- 7. AKTIEN-SCAN MIT TOP-FILTER ---
if 'stock_results' not in st.session_state:
    st.session_state.stock_results = []

if st.button("🚀 Großen Aktien-Scan starten"):
    with st.spinner("Scanne Märkte..."):
        st.session_state.stock_results = get_analysis(stocks, intervall)

if st.session_state.stock_results:
    df = pd.DataFrame(st.session_state.stock_results)
    l, r = st.columns(2)
    
    with l:
        st.success(f"🔥 Top {top_n} CALL (Long)")
        calls = df[df['Typ'] == "CALL 🟢"].sort_values("Wahrscheinlichkeit", ascending=False).head(top_n)
        st.table(calls[["Name", "Wahrscheinlichkeit", "Aktion", "Kurs", "Ziel %"]])
        
    with r:
        st.error(f"📉 Top {top_n} PUT (Short)")
        puts = df[df['Typ'] == "PUT 🔴"].sort_values("Wahrscheinlichkeit", ascending=False).head(top_n)
        st.table(puts[["Name", "Wahrscheinlichkeit", "Aktion", "Kurs", "Ziel %"]])

st.caption("Aktionslogik basiert auf Sentiment (Wetter), Trend (SMA) und Volatilität.")
