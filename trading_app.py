import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")
st.title("📈 Tradingchancen-Rechner")

# --- 1. PARAMETER ---
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h"], index=0)

# --- 2. TICKER-MAP FÜR KLARTEXT-NAMEN ---
@st.cache_data
def get_stock_data():
    # Erweiterte Liste DAX & NASDAQ
    return {
        "ADS.DE": "Adidas", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer", 
        "BMW.DE": "BMW", "RHM.DE": "Rheinmetall", "SAP.DE": "SAP", "SIE.DE": "Siemens",
        "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "TSLA": "Tesla",
        "AMZN": "Amazon", "GOOGL": "Alphabet", "META": "Meta"
    }

stock_map = get_stock_data()

# --- 3. SCANNER LOGIK (VOLATILITÄTSBASIERT) ---
def run_enhanced_scan(ticker_dict, timeframe):
    results = []
    progress_bar = st.progress(0)
    
    for i, (symbol, name) in enumerate(ticker_dict.items()):
        try:
            ticker = yf.Ticker(symbol)
            # Wir laden 20 Tage, um die Volatilität (ATR) zu berechnen
            df = ticker.history(period="20d", interval=timeframe)
            if df.empty or len(df) < 14: continue
            
            current_price = df['Close'].iloc[-1]
            
            # Dynamisches Setup: 
            # Stop-Loss = 2x die durchschnittliche Tagesbewegung (ATR-Ersatz)
            volatilitat = df['High'].max() - df['Low'].min()
            tages_schwankung = volatilitat / 20
            
            sl_distanz = tages_schwankung * 2.5 # Breiterer Stop für 3-10 Tage
            sl = current_price - sl_distanz
            
            # Kursziel = Basierend auf dem Risiko (CRV von 2.0 anstreben)
            tp = current_price + (sl_distanz * 2.0)
            
            # Berechnungen
            risk_per_share = current_price - sl
            shares = int(risiko_eur / risk_per_share) if risk_per_share > 0 else 0
            
            gain_pot = tp - current_price
            crv = gain_pot / risk_per_share
            profit_pct = (gain_pot / current_price) * 100
            
            # Status-Logik: Nur OK, wenn Trend positiv (über 20er Schnitt)
            sma_20 = df['Close'].mean()
            ist_trend_positiv = current_price > sma_20
            
            results.append({
                "Aktie": name,
                "Symbol": symbol,
                "Kurs": round(current_price, 2),
                "Stück": shares,
                "Positionswert": round(shares * current_price, 2),
                "CRV": round(crv, 2),
                "Ziel %": f"{profit_pct:.2f}%",
                "Status": "✅ Bullisch" if ist_trend_positiv else "❌ Bärisch"
            })
        except:
            continue
        progress_bar.progress((i + 1) / len(ticker_dict))
    
    return pd.DataFrame(results)

# --- 4. ANZEIGE ---
if st.button(f"Scan starten ({len(stock_map)} Aktien)"):
    df_results = run_enhanced_scan(stock_map, intervall)
    
    if not df_results.empty:
        st.subheader(f"Ergebnisse (Basis: {intervall})")
        # Spalte "Symbol" ausblenden für bessere Übersicht
        st.dataframe(df_results.drop(columns=["Symbol"]), use_container_width=True)
    else:
        st.warning("Keine Daten gefunden.")

st.info("Hinweis: Das Kursziel (%) ist nun dynamisch und berechnet sich aus der Volatilität der letzten 20 Tage.")
