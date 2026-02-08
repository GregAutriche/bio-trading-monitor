import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. DATEN-LOGIK FÜR DEINE CHAMPIONS ---
def get_champion_stats(tickers):
    data_list = []
    for t_sym in tickers:
        try:
            ticker = yf.Ticker(t_sym)
            df = ticker.history(period="20d")
            name = ticker.info.get('shortName', t_sym)
            if not df.empty and len(df) > 1:
                preis = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                diff = ((preis - prev) / prev) * 100
                
                # RSI / Position im 14-Tage Fenster [cite: 2026-02-07]
                low14, high14 = df['Close'].tail(14).min(), df['Close'].tail(14).max()
                pos_pct = ((preis - low14) / (high14 - low14)) * 100 if high14 != low14 else 50
                
                # Wetter & Trend-Punkt
                wetter = "☀️" if pos_pct > 90 else "🌧️" if pos_pct < 10 else "☁️"
                punkt = "🟢" if diff > 0.01 else "🔴" if diff < -0.01 else "🟡"
                
                # ATR (Volatilität)
                atr = (df['High'] - df['Low']).tail(14).mean()
                
                # Status-Definition [cite: 2026-02-07]
                status = "Normal"
                if pos_pct > 90: status = "EXTREM HOCH"
                elif pos_pct < 10: status = "EXTREM TIEF"
                
                data_list.append({
                    "Trend": f"{wetter}{punkt}",
                    "Name": name,
                    "Preis(EUR)": f"{preis:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    "Pos%": f"{pos_pct:.1f}%",
                    "ATR": round(atr, 2),
                    "Status": status
                })
        except: continue
    return pd.DataFrame(data_list)

# --- 2. HEADER & LEGENDE ---
st.markdown(f"### 🚀 KONTROLLTURM AKTIV | {datetime.now().strftime('%H:%M:%S')}")

with st.expander("📖 Legende: Deine Indikatoren"):
    st.write("**Trend-Vorschau:**")
    st.write("- ☀️/☁️/🌧️: Kurs-Position (RSI) der letzten 14 Tage. [cite: 2026-02-07]")
    st.write("- 🟢/🔴/🟡: Aktueller Tages-Trend (Steigend/Fallend/Neutral).")
    st.write("**Status:** 'EXTREM' warnt bei Werten über 90% oder unter 10%. [cite: 2026-02-07]")

# --- 3. ANZEIGE DER 7 CHAMPIONS ---
# Deine definierten Hidden Champions (Beispiel-Auswahl aus deinen Favoriten)
champions_eu = ["ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE", "VOW3.DE", "BMW.DE"]
champions_us = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

st.write("**Europa: Deine 7 Hidden Champions**")
st.dataframe(get_champion_stats(champions_eu), hide_index=True, use_container_width=True)

st.write("**USA: Deine 7 Hidden Champions**")
st.dataframe(get_champion_stats(champions_us), hide_index=True, use_container_width=True)

# --- 4. BIO-CHECK & REISEN (BACKUP) ---
st.divider()
st.subheader("🧘 Bio-Check & Sicherheit")
st.error("⚠️ **WANDSITZ**: Ruhig atmen! Keine Pressatmung (Blutdruck-Schutz)!")

with st.expander("🛡️ Backup-Informationen (Gesundheit & Reisen)"):
    st.write("🌱 **Blutdruck-Senkung**: Sprossen & Rote Bete in die Ernährung integrieren. [cite: 2025-12-20]")
    st.write("🚫 **Vorsicht**: Keine Mundspülungen (Chlorhexidin), kein Zähneputzen direkt nach dem Essen. [cite: 2025-12-20]")
    st.write("🥜 **Reisen**: Nüsse als gesunder Snack und dein Österreich Ticket sind bereit. [cite: 2026-01-25, 2026-02-03]")
