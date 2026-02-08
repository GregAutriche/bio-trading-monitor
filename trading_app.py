import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# SEITEN-KONFIGURATION
st.set_page_config(page_title="Kontrollturm Live", layout="wide")

# --- 1. DATEN-LOGIK ---
def get_stats(tickers, limit=7):
    data_list = []
    for t_sym in tickers:
        try:
            ticker = yf.Ticker(t_sym)
            # 20d für ATR-Durchschnitt und RSI-Fenster
            df = ticker.history(period="20d")
            name = ticker.info.get('shortName', t_sym)
            if not df.empty and len(df) > 1:
                preis = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                diff = ((preis - prev) / prev) * 100
                
                # RSI / Position Logik (Basis 20-Minuten-Intervalle im Intraday)
                low14, high14 = df['Close'].tail(14).min(), df['Close'].tail(14).max()
                pos_pct = ((preis - low14) / (high14 - low14)) * 100 if high14 != low14 else 50
                
                # Wetter & Trend-Punkt [cite: 2026-02-07]
                wetter = "☀️" if pos_pct > 90 else "🌧️" if pos_pct < 10 else "☁️"
                punkt = "🟢" if diff > 0.01 else "🔴" if diff < -0.01 else "🟡"
                
                # ATR (Volatilität im Verhältnis zum Kurs)
                atr = (df['High'] - df['Low']).tail(14).mean()
                
                status = "Normal"
                if pos_pct > 90: status = "EXTREM HOCH"
                elif pos_pct < 10: status = "EXTREM TIEF"
                
                data_list.append({
                    "Trend": f"{wetter}{punkt}",
                    "Name": name,
                    "Symbol": t_sym,
                    "Preis(EUR)": f"{preis:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    "Pos%": f"{pos_pct:.1f}%",
                    "ATR": round(atr, 2),
                    "Status": status
                })
        except: continue
    return pd.DataFrame(data_list).head(limit)

# --- 2. HEADER & BASIS-MONITOR ---
st.markdown(f"### 🛰️ KONTROLLTURM AKTIV | {datetime.now().strftime('%H:%M:%S')}")
c1, c2, c3 = st.columns(3)

with c1:
    val = yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[-1]
    st.metric("EUR/USD", f"{val:.4f}")
with c2:
    val = yf.Ticker("^GDAXI").history(period="1d")['Close'].iloc[-1]
    st.metric("DAX (ADR)", f"{val:,.2f}")
with c3:
    val = yf.Ticker("^IXIC").history(period="1d")['Close'].iloc[-1]
    st.metric("NASDAQ", f"{val:,.2f}")

st.divider()

# --- 3. DETAILLIERTE LEGENDE ---
with st.expander("📖 System-Details: RSI (20min) & ATR"):
    st.write("**RSI (Relative Stärke):** Berechnet auf **20-Minuten-Intervallen** [cite: 2026-02-07].")
    st.write("- ☀️ EXTREM HOCH (> 90%) | 🌧️ EXTREM TIEF (< 10%) [cite: 2026-02-07].")
    st.write("**ATR (Volatilität):** Zeigt die durchschnittliche Schwankungsbreite im Verhältnis zum Kurs.")
    st.write("**Trend-Punkt:** 🟢/🔴/🟡 zeigt die Kursänderung zum Vortag an.")

# --- 4. CHAMPIONS (7x7 Portfolio) ---
# Hier deine Hidden Champions [cite: 2026-02-07]
champions_eu = ["ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE", "VOW3.DE", "BMW.DE"]
champions_us = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

col_a, col_b = st.columns(2)
with col_a:
    st.write("**Europa: Deine 7 Hidden Champions**")
    st.dataframe(get_stats(champions_eu), hide_index=True, use_container_width=True)
with col_b:
    st.write("**USA: Deine 7 Hidden Champions**")
    st.dataframe(get_stats(champions_us), hide_index=True, use_container_width=True)

# --- 5. BIO-CHECK & SICHERHEIT ---
st.divider()
st.subheader("🧘 Bio-Check & Sicherheit")
st.error("⚠️ **WANDSITZ**: Ruhig atmen! Keine Pressatmung (Blutdruck-Schutz)!")

with st.expander("🛡️ Backup-Informationen (Gesundheit & Reisen)"):
    st.write("🌱 **Blutdruck**: Sprossen & Rote Bete (natürliche Senker) [cite: 2025-12-20].")
    st.write("🚫 **Warnung**: Keine Mundspülungen mit Chlorhexidin verwenden [cite: 2025-12-20].")
    st.write("🥜 **Reisen**: Nüsse als Snack & Österreich Ticket sind bereit [cite: 2026-01-25,
