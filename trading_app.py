import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. DATEN-LOGIK MIT SYMBOLEN ---
def get_monitor_stats(tickers):
    data_list = []
    for t_sym in tickers:
        try:
            ticker = yf.Ticker(t_sym)
            df = ticker.history(period="20d")
            name = ticker.info.get('shortName', t_sym)
            if not df.empty:
                preis = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                diff = ((preis - prev) / prev) * 100
                
                # Wetter & RSI-Logik [cite: 2026-02-07]
                low14, high14 = df['Close'].tail(14).min(), df['Close'].tail(14).max()
                pos_pct = ((preis - low14) / (high14 - low14)) * 100 if high14 != low14 else 50
                wetter = "☀️" if pos_pct > 90 else "🌧️" if pos_pct < 10 else "☁️"
                
                # Farb-Punkt Logik (Trend heute)
                punkt = "🟢" if diff > 0.01 else "🔴" if diff < -0.01 else "🟡"
                
                # ATR (Volatilität)
                atr = (df['High'] - df['Low']).tail(14).mean()
                
                status = "Normal"
                if pos_pct > 90: status = "EXTREM HOCH"
                elif pos_pct < 10: status = "EXTREM TIEF"
                
                data_list.append({
                    "Trend": f"{wetter} {punkt}",
                    "Name": name,
                    "Preis(EUR)": f"{preis:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    "Pos%": f"{pos_pct:.1f}%",
                    "ATR": round(atr, 2),
                    "Status": status
                })
        except: continue
    return pd.DataFrame(data_list)

# --- 2. LEGENDE & HEADER ---
st.markdown("### 🚀 KONTROLLTURM AKTIV")
with st.expander("📖 Legende"):
    st.write("☀️/☁️/🌧️ = Kurs-Position (RSI) | 🟢/🔴/🟡 = Trend heute")

# --- 3. CHAMPIONS (7x EUROPA & 7x USA) ---
# Hier sind wieder alle 7 pro Region enthalten
europa = ["OTP.BU", "MOL.BU", "ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE"]
usa = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

st.markdown("#### 🏆 CHAMPIONS (7x7 Portfolio):")

st.write("**Europa**")
# hide_index=True entfernt die Ziffern 0, 1, 2... am Rand
st.dataframe(get_monitor_stats(europa), hide_index=True)

st.write("**USA**")
st.dataframe(get_monitor_stats(usa), hide_index=True)

st.info("🧘 Routine: WANDSITZ & RUHIG ATMEN! [cite: 2025-12-20]")
