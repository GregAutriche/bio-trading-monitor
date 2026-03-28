import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. SETUP ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: gray;'>Update: {last_update}</p>", unsafe_allow_html=True)

st.title("🚀 Tradingchancen: Top CALL & PUT")

# --- 2. SIDEBAR ---
st.sidebar.header("Einstellungen")
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)
# Der Slider für die Top-Auswahl
top_n = st.sidebar.slider("Top-Signale anzeigen", min_value=1, max_value=10, value=5)

# --- 3. TICKER-LISTEN ---
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX 50", "^NSEI": "NIFTY 50", "XU100.IS": "BIST 100"}
forex = {"EURUSD=X": "EUR/USD"}
stocks = {
    "ADS.DE": "Adidas", "ALV.DE": "Allianz", "SAP.DE": "SAP", "RHM.DE": "Rheinmetall", 
    "NVDA": "Nvidia", "AAPL": "Apple", "MSFT": "Microsoft", "TSLA": "Tesla", "AMZN": "Amazon",
    "GOOGL": "Alphabet", "META": "Meta", "VOW3.DE": "VW", "DBK.DE": "Deutsche Bank"
}

# --- 4. ANALYSE-FUNKTION ---
def get_analysis(ticker_dict, timeframe, is_fx=False):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="1mo" if "m" in timeframe else "6mo", interval=timeframe)
            if len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            sma = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma
            
            # Einfacher Wahrscheinlichkeits-Score
            score = 50
            if is_bullish: score += 20
            else: score += 10 # Basis-Score
            
            # RSI-Berechnung
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            if (is_bullish and 50 < rsi < 70) or (not is_bullish and 30 < rsi < 50): score += 20
            
            vol = hist['High'].rolling(10).std().iloc[-1]
            sl_dist = vol * 2
            risk_unit = sl_dist if sl_dist > 0 else cp * 0.01
            shares = round(risiko_eur / (risk_unit * 10000), 4) if is_fx else int(risiko_eur / risk_unit)

            data_list.append({
                "Aktie/Name": name,
                "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{min(score, 98)}%",
                "Prob_Value": score, # Nur zum Sortieren
                "Kurs": round(cp, 5 if is_fx else 2),
                "Stück/Lots": shares,
                "Ziel %": f"{abs((sl_dist*2.5)/cp)*100:.2f}%"
            })
        except: continue
    return data_list

# --- 5. DASHBOARD & FEHLERBEHEBUNG ---
# Vorab-Initialisierung, um den NameError zu vermeiden
all_data = []

# Forex & Indizes (werden immer geladen)
fx_data = get_analysis(forex, intervall, is_fx=True)
if fx_data:
    st.metric(f"{fx_data[0]['Aktie/Name']}", fx_data[0]['Kurs'], delta=fx_data[0]['Typ'])

st.divider()

if st.button("Aktien-Scan starten"):
    all_data = get_analysis(stocks, intervall)
    
    if all_data:
        df = pd.DataFrame(all_data)
        col_call, col_put = st.columns(2)
        
        with col_call:
            st.success(f"🔥 Top {top_n} CALL Signale")
            calls = df[df['Typ'] == "CALL 🟢"].sort_values(by="Prob_Value", ascending=False).head(top_n)
            st.table(calls[["Aktie/Name", "Wahrscheinlichkeit", "Kurs", "Ziel %"]])
            
        with col_put:
            st.error(f"📉 Top {top_n} PUT Signale")
            puts = df[df['Typ'] == "PUT 🔴"].sort_values(by="Prob_Value", ascending=False).head(top_n)
            st.table(puts[["Aktie/Name", "Wahrscheinlichkeit", "Kurs", "Ziel %"]])
    else:
        st.warning("Keine Daten gefunden. Bitte Intervall prüfen.")

st.caption("Wahrscheinlichkeit berechnet aus Trend (SMA) und Momentum (RSI).")
