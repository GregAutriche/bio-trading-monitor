import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Trading-Scanner 3-10 Tage", layout="wide")
st.title("📈 Tradingchancen-Rechner")
st.write("Basierend auf dem 500€ Risiko-Modell (Haltedauer 3-10 Tage)")

# --- 2. EINSTELLUNGEN IN DER SIDEBAR ---
st.sidebar.header("Parameter")
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
st.sidebar.markdown("---")
st.sidebar.write("3-5-7 Regel aktiv: Ziel > 7%")

# --- 3. WATCHLIST DEFINITION ---
watchlist = {
    "NVDA":    {"sl": 120.00, "tp": 150.00},
    "SAP.DE":  {"sl": 170.00, "tp": 200.00},
    "RHM.DE":  {"sl": 480.00, "tp": 550.00},
    "AAPL":    {"sl": 185.00, "tp": 215.00}
}

# --- 4. SCANNER LOGIK ---
def run_scan():
    results = []
    
    with st.spinner('Lade Marktdaten von Yahoo Finance...'):
        for symbol, params in watchlist.items():
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period="5d")
                
                if df.empty:
                    continue
                
                current_price = df['Close'].iloc[-1]
                sl = params['sl']
                tp = params['tp']
                
                # Risiko-Kalkulation
                risk_per_share = abs(current_price - sl)
                shares = int(risiko_eur / risk_per_share) if risk_per_share > 0 else 0
                
                # Kennzahlen
                gain_pot = abs(tp - current_price)
                crv = gain_pot / risk_per_share if risk_per_share > 0 else 0
                profit_pct = (gain_pot / current_price) * 100
                
                results.append({
                    "Symbol": symbol,
                    "Kurs": round(current_price, 2),
                    "Stück": shares,
                    "Positionswert": round(shares * current_price, 2),
                    "CRV": round(crv, 2),
                    "Ziel %": f"{profit_pct:.2f}%",
                    "Status": "✅ OK" if profit_pct >= 7 else "⚠️ Ziel < 7%"
                })
            except Exception as e:
                st.error(f"Fehler bei {symbol}: {e}")

    return pd.DataFrame(results)

# --- 5. ÜBERSICHT ANZEIGEN ---
if st.button("Jetzt Scan starten"):
    df_results = run_scan()
    
    if not df_results.empty:
        # Ergebnisse als Tabelle
        st.dataframe(df_results, use_container_width=True)
        
        # Highlight: Beste Chance (höchstes CRV)
        best_trade = df_results.loc[df_results['CRV'].idxmax()]
        st.success(f"Beste Chance aktuell: **{best_trade['Symbol']}** mit einem CRV von {best_trade['CRV']}")
    else:
        st.warning("Keine Daten gefunden. Bitte Internetverbindung prüfen.")

# Footer
st.markdown("---")
st.caption("Datenquelle: Yahoo Finance. Alle Berechnungen ohne Gewähr.")
