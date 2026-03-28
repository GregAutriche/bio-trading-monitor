import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")
st.title("📈 Tradingchancen-Rechner")
st.write("Basierend auf dem 500€ Risiko-Modell (Haltedauer 3-10 Tage)")

# --- 2. SIDEBAR: EINSTELLUNGEN & INTERVAL ---
st.sidebar.header("Scan-Parameter")
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
# NEU: Intervall-Grundlage
intervall = st.sidebar.selectbox("Scan-Intervall (Grundlage)", 
                               options=["1d", "1h", "15m"], 
                               index=0, 
                               help="1d = Tagesbasis (Swing), 1h/15m = Intraday-Trends")

# --- 3. AUTOMATISCHE TICKER-LISTEN ---
@st.cache_data
def get_tickers():
    # DAX 40 (vereinfachte Liste, da sich Komponenten ändern können)
    dax_tickers = ["ADS.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CON.DE", "DB1.DE", "DBK.DE", "DPW.DE", "DTE.DE", "EOAN.DE", "FRE.DE", "HEI.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "VOW3.DE", "RHM.DE"]
    # NASDAQ 100 (Top-Werte als Beispiel, da volle Liste >100 API-Calls braucht)
    nasdaq_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "PEP", "AVGO", "COST", "NFLX", "ADBE"]
    return dax_tickers + nasdaq_tickers

all_tickers = get_tickers()

# --- 4. SCANNER LOGIK MIT INTERVALL ---
def run_scan(ticker_list, timeframe):
    results = []
    progress_bar = st.progress(0)
    
    for i, symbol in enumerate(ticker_list):
        try:
            ticker = yf.Ticker(symbol)
            # Nutzt das gewählte Intervall (z.B. '1d' für 3-10 Tage Haltedauer)
            df = ticker.history(period="60d", interval=timeframe)
            
            if df.empty or len(df) < 2: continue
            
            current_price = df['Close'].iloc[-1]
            
            # AUTOMATISCHE SL/TP LOGIK (Beispiel: SL bei 5% Abstand, TP bei 15%)
            # Da wir keine manuellen Werte für 140+ Aktien eingeben können:
            sl = current_price * 0.95 
            tp = current_price * 1.15
            
            risk_per_share = abs(current_price - sl)
            shares = int(risiko_eur / risk_per_share) if risk_per_share > 0 else 0
            
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
                "Status": "✅ OK" if crv >= 1.5 else "⚠️ CRV schwach"
            })
            progress_bar.progress((i + 1) / len(ticker_list))
        except:
            continue

    return pd.DataFrame(results)

# --- 5. ÜBERSICHT ---
if st.button(f"Scan starten ({len(all_tickers)} Aktien auf {intervall}-Basis)"):
    df_results = run_scan(all_tickers, intervall)
    
    if not df_results.empty:
        st.subheader(f"Ergebnisse (Grundlage: {intervall})")
        st.dataframe(df_results.sort_values(by="CRV", ascending=False), use_container_width=True)
        
        best_trade = df_results.loc[df_results['CRV'].idxmax()]
        st.success(f"Top-Chance (höchstes CRV): **{best_trade['Symbol']}**")
    else:
        st.warning("Keine Daten gefunden.")

st.caption(f"Aktueller Stand: {pd.Timestamp.now().strftime('%d.%m.%Y %H:%M')} | Intervall: {intervall}")
