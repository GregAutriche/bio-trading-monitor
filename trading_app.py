import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SETUP ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: gray;'>Update: {last_update}</p>", unsafe_allow_html=True)

st.title("🚀 Trading-Monitor: Strategie 3-10 Tage")

# --- 2. SIDEBAR ---
st.sidebar.header("Konfiguration")
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)
top_n = st.sidebar.slider("Anzahl Top-Signale", 1, 10, 5)

# --- 3. ANALYSE-LOGIK ---
def get_analysis(ticker_dict, timeframe, is_fx=False):
    data_list = []
    # Wetter/Sentiment-Bonus (fest auf +5 für sonniges Börsengemüt)
    wetter_bonus = 5 
    
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            # WAHRSCHEINLICHKEIT & AKTION
            prob = 50 + (25 if is_bullish else 10) + wetter_bonus
            if prob >= 75: action = "🔥 AGGRESSIV"
            elif prob >= 60: action = "✅ HANDELN"
            else: action = "🛑 WARTEN"
            
            # SL/TP Berechnung (Volatilitätsbasiert)
            vol = hist['High'].rolling(10).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.02
            sl = cp - sl_dist if is_bullish else cp + sl_dist
            tp = cp + (sl_dist * 2.5) if is_bullish else cp - (sl_dist * 2.5)
            
            risk_unit = abs(cp - sl)
            shares = round(risiko_eur / (risk_unit * 10000), 4) if is_fx else int(risiko_eur / risk_unit)

            data_list.append({
                "Name": name, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{min(prob, 99)}%",
                "Aktion": action, "Kurs": round(cp, 5 if is_fx else 2),
                "Stück/Lots": shares, "Ziel %": f"{abs((tp-cp)/cp)*100:.2f}%",
                "SL": sl, "TP": tp, "Hist": hist
            })
        except: continue
    return data_list

# --- 4. EUR/USD SEKTION MIT GRAFIK ---
st.subheader("💱 EUR/USD Live-Analyse & Grafik")
fx_res = get_analysis({"EURUSD=X": "EUR/USD"}, intervall, is_fx=True)

if fx_res:
    res = fx_res[0] # Erster Treffer
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kurs", f"{res['Kurs']:.5f}")
    c2.metric("Wahrscheinlichkeit", res['Wahrscheinlichkeit'])
    c3.metric("Aktion", res['Aktion'])
    c4.info(f"**Lots:** {res['Stück/Lots']}")

    # --- DIE GRAFIK ---
    fig = go.Figure(data=[go.Candlestick(
        x=res['Hist'].index, open=res['Hist']['Open'], high=res['Hist']['High'],
        low=res['Hist']['Low'], close=res['Hist']['Close'], name="EUR/USD"
    )])
    
    # Einstieg, SL und TP Linien
    fig.add_hline(y=res['Kurs'], line_color="blue", annotation_text="Einstieg")
    fig.add_hline(y=res['TP'], line_dash="dash", line_color="green", annotation_text="Ziel (TP)")
    fig.add_hline(y=res['SL'], line_dash="dash", line_color="red", annotation_text="Stopp (SL)")
    
    fig.update_layout(height=400, template="plotly_dark", margin=dict(l=0, r=0, t=30, b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 5. INDIZES ---
st.subheader("📊 Indizes Wahrscheinlichkeits-Check")
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX 50", "^NSEI": "NIFTY 50", "XU100.IS": "BIST 100"}
idx_data = get_analysis(indices, intervall)
if idx_data:
    st.table(pd.DataFrame(idx_data)[["Name", "Kurs", "Typ", "Wahrscheinlichkeit", "Aktion", "Ziel %"]])

st.divider()

# --- 6. AKTIEN-SCAN ---
stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall", "AAPL": "Apple", "TSLA": "Tesla"}

if st.button("🚀 Großen Aktien-Scan starten"):
    stock_results = get_analysis(stocks, intervall)
    if stock_results:
        df = pd.DataFrame(stock_results)
        l, r = st.columns(2)
        with l:
            st.success(f"🔥 Top {top_n} CALL (Long)")
            st.table(df[df['Typ'] == "CALL 🟢"].sort_values("Wahrscheinlichkeit", ascending=False).head(top_n)[["Name", "Wahrscheinlichkeit", "Aktion", "Kurs"]])
        with r:
            st.error(f"📉 Top {top_n} PUT (Short)")
            st.table(df[df['Typ'] == "PUT 🔴"].sort_values("Wahrscheinlichkeit", ascending=False).head(top_n)[["Name", "Wahrscheinlichkeit", "Aktion", "Kurs"]])

st.caption("Grafik zeigt EUR/USD Candlesticks mit statischen Trading-Ebenen (TP/SL/Entry).")
