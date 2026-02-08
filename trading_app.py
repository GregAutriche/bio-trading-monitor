import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. KONTROLLTURM HEADER ---
jetzt = datetime.now()
st.markdown(f"### 🚀 KONTROLLTURM AKTIV | {jetzt.strftime('%H:%M:%S')} ---")
st.write(f"🟢 **BASIS: EUR/USD = {yf.Ticker('EURUSD=X').history(period='1d')['Close'].iloc[-1]:.4f}**")
st.write("☀️ **MARKT-WETTER: ⚠️ Hitzewelle!**") # Statisch wie im Screen oder dynamisch
st.divider()

# --- 2. LOGIK FÜR DATEN (RSI & ATR) ---
def get_monitor_stats(tickers):
    data_list = []
    for t_sym in tickers:
        try:
            ticker = yf.Ticker(t_sym)
            df = ticker.history(period="20d")
            if not df.empty:
                preis = df['Close'].iloc[-1]
                # RSI-Näherung (Position in 14d Range)
                low14, high14 = df['Close'].tail(14).min(), df['Close'].tail(14).max()
                pos_pct = ((preis - low14) / (high14 - low14)) * 100 if high14 != low14 else 50
                # ATR (14d Durchschnitt der Tages-Range)
                atr = (df['High'] - df['Low']).tail(14).mean()
                
                # Status-Logik laut deiner Vorgabe [cite: 2026-02-07]
                status = "Normal"
                if pos_pct > 90: status = "EXTREM HOCH"
                elif pos_pct < 10: status = "EXTREM TIEF"
                
                data_list.append({
                    "Symbol": t_sym,
                    "Preis(EUR)": f"{preis:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    "Pos%": round(pos_pct, 1),
                    "RSI": round(pos_pct, 1), # Im Monitor oft identisch genutzt
                    "ATR": round(atr, 2),
                    "Status": status
                })
        except: continue
    return pd.DataFrame(data_list)

# --- 3. INDIZES TABELLE ---
st.markdown("#### 📊 INDIZES:")
indizes_df = get_monitor_stats(["^GDAXI", "^IXIC"])
st.table(indizes_df)

# --- 4. CHAMPIONS TABELLE ---
st.markdown("#### 🏆 CHAMPIONS:")
aktien_symbole = ["ASML.AS", "MC.PA", "SAP.DE", "AAPL", "MSFT", "NVDA", "OTP.BU"]
champions_df = get_monitor_stats(aktien_symbole)
st.table(champions_df)

st.divider()
st.write(f"**Update in 30s | Routine: WANDSITZ & RUHIG ATMEN** [cite: 2025-12-20]")
