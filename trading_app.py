import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta  # Für technische Indikatoren (pip install pandas_ta)
from datetime import datetime

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: gray;'>Update: {last_update}</p>", unsafe_allow_html=True)

st.title("🚀 Tradingchancen-Rechner mit Wahrscheinlichkeit")

# --- 2. SIDEBAR ---
st.sidebar.header("Parameter")
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)

# --- 3. TICKER-LISTEN ---
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX 50", "^NSEI": "NIFTY 50", "XU100.IS": "BIST 100"}
forex = {"EURUSD=X": "EUR/USD"}
stocks = {"ADS.DE": "Adidas", "ALV.DE": "Allianz", "SAP.DE": "SAP", "RHM.DE": "Rheinmetall", "NVDA": "Nvidia", "AAPL": "Apple", "TSLA": "Tesla"}

# --- 4. SCANNER LOGIK MIT WAHRSCHEINLICHKEIT ---
def get_analysis(ticker_dict, timeframe, is_fx=False):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            # Wir benötigen genug Historie für den RSI (mind. 14 Perioden)
            hist = t.history(period="1mo" if "m" in timeframe else "6mo", interval=timeframe)
            if len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            
            # --- WAHRSCHEINLICHKEITS-SCORE (0-100%) ---
            score = 0
            # 1. Trend (SMA 20) - Gewichtung 40%
            sma = hist['Close'].rolling(20).mean().iloc[-1]
            if cp > sma: score += 40
            
            # 2. Momentum (RSI 14) - Gewichtung 30%
            # RSI zwischen 40 und 60 ist ideal für Trendfortsetzung
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            if 40 < rsi < 70: score += 30
            
            # 3. Volatilitäts-Stabilität - Gewichtung 30%
            # Check, ob der Schlusskurs nah am Tageshoch liegt
            day_range = hist['High'].iloc[-1] - hist['Low'].iloc[-1]
            if day_range > 0 and (cp - hist['Low'].iloc[-1]) / day_range > 0.6:
                score += 30
            
            # Setup-Berechnung
            volatility = hist['High'].rolling(10).std().iloc[-1]
            sl_dist = volatility * 2
            sl = cp - sl_dist
            tp = cp + (sl_dist * 2.5)
            
            risk_unit = abs(cp - sl)
            shares = int(risiko_eur / risk_unit) if risk_unit > 0 else 0
            if is_fx: shares = round(risiko_eur / (risk_unit * 10000), 2)

            data_list.append({
                "Name": name,
                "Kurs": round(cp, 4 if is_fx else 2),
                "Stück/Lots": shares,
                "Wahrscheinlichkeit": f"{score}%",
                "Status": "✅ Bullisch" if score >= 60 else "⚠️ Neutral" if score >= 40 else "❌ Schwach",
                "Ziel %": f"{((tp-cp)/cp)*100:.2f}%",
                "CRV": round((tp-cp)/risk_unit, 2)
            })
        except: continue
    return data_list

# --- 5. ANZEIGE ---
# Forex Sektion
fx_res = get_analysis(forex, intervall, is_fx=True)
if fx_res:
    f = fx_res[0]
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Währung: {f['Name']}", f['Kurs'])
    c2.metric("Wahrscheinlichkeit", f['Wahrscheinlichkeit'])
    c3.write(f"**Empfehlung:** {f['Status']}  \n**Einsatz:** {f['Stück/Lots']} Lots")

st.divider()

# Indizes Sektion
st.subheader("📊 Indizes Wahrscheinlichkeits-Check")
idx_data = get_analysis(indices, intervall)
if idx_data:
    st.dataframe(pd.DataFrame(idx_data), use_container_width=True)

st.divider()

# Aktien Sektion
if st.button("Großen Aktien-Scan starten"):
    stock_data = get_analysis(stocks, intervall)
    if stock_data:
        df = pd.DataFrame(stock_data).sort_values(by="Wahrscheinlichkeit", ascending=False)
        st.dataframe(df, use_container_width=True)

st.caption("Wahrscheinlichkeit basiert auf Trend-Konfluenz (SMA), RSI-Momentum und Candle-Close-Stärke.")
