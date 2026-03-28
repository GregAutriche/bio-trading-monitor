import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURATION & STYLING ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")

# Anzeige des letzten Updates ganz oben
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: gray;'>Letztes Update: {last_update}</p>", unsafe_allow_html=True)

st.title("🚀 Tradingchancen-Rechner")

# --- 2. SIDEBAR PARAMETER ---
st.sidebar.header("Scan-Parameter")
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
# NEU: 5-Minuten Intervall hinzugefügt
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)

# --- 3. DATEN-MAPPING (INDIZES & FOREX) ---
# Ticker-Listen
indices_tickers = {
    "^GDAXI": "DAX", "^IXIC": "NASDAQ Composite", "^STOXX50E": "EURO STOXX 50", 
    "^NSEI": "NIFTY 50", "XU100.IS": "BIST 100"
}
forex_ticker = {"EURUSD=X": "EUR/USD"}

# Aktien-Liste (Auszug DAX/NASDAQ)
stock_map = {
    "ADS.DE": "Adidas", "ALV.DE": "Allianz", "BAS.DE": "BASF", "SAP.DE": "SAP", 
    "RHM.DE": "Rheinmetall", "NVDA": "Nvidia", "AAPL": "Apple", "MSFT": "Microsoft",
    "TSLA": "Tesla", "AMZN": "Amazon"
}

# --- 4. HILFSFUNKTION FÜR SETUPS ---
def get_setup_data(ticker_dict, timeframe, is_forex=False):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            # Bei 5m Intervall laden wir nur 5 Tage Historie für Speed
            hist = t.history(period="5d" if "m" in timeframe else "60d", interval=timeframe)
            if hist.empty: continue
            
            cp = hist['Close'].iloc[-1]
            high_20 = hist['High'].max()
            low_20 = hist['Low'].min()
            volatility = (high_20 - low_20) / 10 # Annäherung ATR
            
            # Setup Logik (ATR-basiert)
            sl_dist = volatility * 1.5
            sl = cp - sl_dist
            tp = cp + (sl_dist * 2.5) # CRV 2.5
            
            risk_unit = cp - sl
            shares = int(risiko_eur / risk_unit) if risk_unit > 0 else 0
            
            # Bei Forex ist die Stückzahl anders skaliert (Lots)
            if is_forex: shares = round(risiko_eur / (risk_unit * 10000), 2)
            
            data_list.append({
                "Name": name, "Kurs": round(cp, 4 if is_forex else 2), 
                "Stück/Lots": shares, "CRV": round((tp-cp)/risk_unit, 2),
                "Ziel %": f"{((tp-cp)/cp)*100:.2f}%",
                "Status": "✅ Long" if cp > hist['Close'].mean() else "❌ Short"
            })
        except: continue
    return data_list

# --- 5. DASHBOARD LAYOUT ---

# A. FOREX & INDIZES (OBERE SEKTION)
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("💱 Forex")
    fx_data = get_setup_data(forex_ticker, intervall, is_forex=True)
    if fx_data:
        st.metric(f"{fx_data[0]['Name']}", fx_data[0]['Kurs'])
        st.write(f"**Chance:** {fx_data[0]['Status']} | **Ziel:** {fx_data[0]['Ziel %']}")
        st.caption(f"SL: {fx_data[0]['Stück/Lots']} Lots für {risiko_eur}€ Risiko")

with col2:
    st.subheader("📊 Indizes Übersicht")
    idx_results = get_setup_data(indices_tickers, intervall)
    if idx_results:
        idx_df = pd.DataFrame(idx_results)
        st.dataframe(idx_df[["Name", "Kurs", "Status", "Ziel %", "CRV"]], use_container_width=True)

st.divider()

# B. AKTIEN SCAN (UNTERE SEKTION)
st.subheader(f"🔍 Aktien-Scan ({len(stock_map)} Titel auf {intervall}-Basis)")
if st.button("Großen Aktien-Scan starten"):
    stock_results = get_setup_data(stock_map, intervall)
    if stock_results:
        st.dataframe(pd.DataFrame(stock_results), use_container_width=True)
    else:
        st.error("Keine Daten für Aktien-Scan verfügbar.")

st.markdown("---")
st.caption("Grundlage: Yahoo Finance Live-Daten. Stückzahlen berechnet auf Basis Ihres 500€ Risikos pro Trade.")
