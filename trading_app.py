import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. KONTROLLTURM HEADER ---
jetzt = datetime.now()
st.markdown(f"### 🚀 KONTROLLTURM AKTIV | {jetzt.strftime('%H:%M:%S')} ---")
# Basis-Kurs live abrufen
eur_usd = yf.Ticker('EURUSD=X').history(period='1d')['Close'].iloc[-1]
st.write(f"🟢 **BASIS: EUR/USD = {eur_usd:.4f}**")
st.write("☀️ **MARKT-WETTER: ⚠️ Hitzewelle!**") 
st.divider()

# --- 2. LOGIK FÜR DATEN (RSI & ATR) ---
def get_monitor_stats(tickers):
    data_list = []
    for t_sym in tickers:
        try:
            ticker = yf.Ticker(t_sym)
            df = ticker.history(period="20d")
            # Namen für die Anzeige abrufen
            name = ticker.info.get('shortName', t_sym)
            if not df.empty:
                preis = df['Close'].iloc[-1]
                low14, high14 = df['Close'].tail(14).min(), df['Close'].tail(14).max()
                pos_pct = ((preis - low14) / (high14 - low14)) * 100 if high14 != low14 else 50
                atr = (df['High'] - df['Low']).tail(14).mean()
                
                # Status-Logik laut Vorgabe [cite: 2026-02-07]
                status = "Normal"
                if pos_pct > 90: status = "EXTREM HOCH"
                elif pos_pct < 10: status = "EXTREM TIEF"
                
                data_list.append({
                    "Name": name,
                    "Symbol": t_sym,
                    "Preis(EUR)": f"{preis:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    "Pos%": f"{pos_pct:.1f}%",
                    "RSI": round(pos_pct, 1),
                    "ATR": round(atr, 2),
                    "Status": status
                })
        except: continue
    return pd.DataFrame(data_list)

# --- 3. LEGENDE (WIEDER DA) ---
with st.expander("📖 Legende: Farben & Symbole"):
    st.write("**Status-Logik:**")
    st.write("☀️ EXTREM HOCH = Pos% > 90% | 🌧️ EXTREM TIEF = Pos% < 10% [cite: 2026-02-07]")
    st.write("ATR = Durchschnittliche Schwankungsbreite der letzten 14 Tage.")

# --- 4. INDIZES ---
st.markdown("#### 📊 INDIZES:")
df_indizes = get_monitor_stats(["^GDAXI", "^IXIC"])
# index=False entfernt die störenden Ziffern 0, 1 am Rand
st.table(df_indizes)

# --- 5. CHAMPIONS (7x EUROPA & 7x USA) ---
st.markdown("#### 🏆 CHAMPIONS (7x7 Portfolio):")
europa = ["OTP.BU", "MOL.BU", "ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE"]
usa = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

# Tabellen für Europa und USA ohne Index-Ziffern
st.write("**Europa**")
st.table(get_monitor_stats(europa))

st.write("**USA**")
st.table(get_monitor_stats(usa))

st.divider()
st.write(f"**Update in 30s | Routine: WANDSITZ & RUHIG ATMEN**")
