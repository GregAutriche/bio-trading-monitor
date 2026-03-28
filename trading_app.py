import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SETUP & TIMER ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: gray;'>Letztes Update: {last_update}</p>", unsafe_allow_html=True)

st.title("🚀 Trading-Monitor: Strategie 3-10 Tage")

# --- 2. SIDEBAR PARAMETER ---
st.sidebar.header("Konfiguration")
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)
top_n = st.sidebar.slider("Top-Signale (Slider)", min_value=1, max_value=10, value=5)

# --- 3. TICKER-LISTEN ---
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX 50", "^NSEI": "NIFTY 50", "XU100.IS": "BIST 100"}
forex_ticker = "EURUSD=X"
stocks = {
    "ADS.DE": "Adidas", "ALV.DE": "Allianz", "SAP.DE": "SAP", "RHM.DE": "Rheinmetall", 
    "NVDA": "Nvidia", "AAPL": "Apple", "MSFT": "Microsoft", "TSLA": "Tesla", "AMZN": "Amazon",
    "GOOGL": "Alphabet", "META": "Meta", "VOW3.DE": "VW", "DBK.DE": "Deutsche Bank"
}

# --- 4. ANALYSE-LOGIK ---
def get_analysis(ticker_dict, timeframe, is_fx=False):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            # Historie laden (30 Einheiten für Indikatoren)
            hist = t.history(period="60d", interval=timeframe)
            if len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            sma = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma
            
            # WAHRSCHEINLICHKEITS-SCORE
            score = 50
            if is_bullish: score += 20
            
            # Manueller RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            if (is_bullish and 50 < rsi < 75) or (not is_bullish and 25 < rsi < 50): score += 30
            
            # Volatilität für SL/TP
            vol = hist['High'].rolling(10).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.02
            
            sl = cp - sl_dist if is_bullish else cp + sl_dist
            tp = cp + (sl_dist * 2.5) if is_bullish else cp - (sl_dist * 2.5)
            
            risk_unit = abs(cp - sl)
            # Forex Lots (5 Nachkommastellen Genauigkeit)
            shares = round(risiko_eur / (risk_unit * 10000), 4) if is_fx else int(risiko_eur / risk_unit)

            data_list.append({
                "Name": name, 
                "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{min(score, 98)}%",
                "Prob_Sort": score,
                "Kurs": round(cp, 5 if is_fx else 2),
                "Stück/Lots": shares,
                "Ziel %": f"{abs((tp-cp)/cp)*100:.2f}%",
                "SL": round(sl, 5 if is_fx else 2),
                "TP": round(tp, 5 if is_fx else 2),
                "Hist": hist
            })
        except: continue
    return data_list

# --- 5. EUR/USD SETUP (OBEN) ---
st.subheader("💱 EUR/USD Live-Analyse")
fx_data = get_analysis({forex_ticker: "EUR/USD"}, intervall, is_fx=True)

if fx_data:
    res = fx_data[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kurs", f"{res['Kurs']:.5f}")
    c2.metric("Wahrscheinlichkeit", res['Wahrscheinlichkeit'])
    c3.metric("Ziel (TP)", f"{res['TP']:.5f}")
    c4.metric("Stopp (SL)", f"{res['SL']:.5f}")
    
    # NEU: Nur ein einfacher Candlestick-Chart mit SL/TP ohne extra Markierungen
    fig = go.Figure(data=[go.Candlestick(x=res['Hist'].index, open=res['Hist']['Open'], 
                    high=res['Hist']['High'], low=res['Hist']['Low'], close=res['Hist']['Close'], name="EUR/USD")])
    fig.add_hline(y=res['TP'], line_color="green", line_dash="dash", annotation_text="TP")
    fig.add_hline(y=res['SL'], line_color="red", line_dash="dash", annotation_text="SL")
    fig.update_layout(height=350, template="plotly_dark", margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 6. INDIZES ---
st.subheader("📊 Indizes Wahrscheinlichkeits-Check")
idx_res = get_analysis(indices, intervall)
if idx_res:
    st.table(pd.DataFrame(idx_res)[["Name", "Kurs", "Typ", "Wahrscheinlichkeit", "Ziel %"]])

st.divider()

# --- 7. AKTIEN-SCAN MIT TOP-FILTER ---
if 'stock_results' not in st.session_state:
    st.session_state.stock_results = []

if st.button("🚀 Großen Aktien-Scan starten"):
    st.session_state.stock_results = get_analysis(stocks, intervall)

if st.session_state.stock_results:
    df = pd.DataFrame(st.session_state.stock_results)
    l, r = st.columns(2)
    
    with l:
        st.success(f"🔥 Top {top_n} CALL (Long)")
        calls = df[df['Typ'] == "CALL 🟢"].sort_values("Prob_Sort", ascending=False).head(top_n)
        st.table(calls[["Name", "Wahrscheinlichkeit", "Kurs", "Ziel %"]])
        
    with r:
        st.error(f"📉 Top {top_n} PUT (Short)")
        puts = df[df['Typ'] == "PUT 🔴"].sort_values("Prob_Sort", ascending=False).head(top_n)
        st.table(puts[["Name", "Wahrscheinlichkeit", "Kurs", "Ziel %"]])

st.caption("Fokus auf klare Zahlenwerte und Wahrscheinlichkeiten. Grafik auf das Wesentliche reduziert.")
