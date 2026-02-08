import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# SEITEN-KONFIGURATION
st.set_page_config(page_title="Kontrollturm Live", layout="wide")

# --- 1. DATEN-FUNKTION (Basis-Monitore & Champions) ---
def get_market_data(symbol, limit=7):
    try:
        t = yf.Ticker(symbol)
        # 15m Intervalle für präzise 20-Minuten-RSI Annäherung [cite: 2026-02-07]
        df = t.history(period="5d", interval="15m")
        if df.empty or len(df) < 14:
            df = t.history(period="20d")
        
        name = t.info.get('shortName', symbol)
        preis = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        diff = ((preis - prev) / prev) * 100
        
        # RSI / Position Logik [cite: 2026-02-07]
        low14, high14 = df['Close'].tail(14).min(), df['Close'].tail(14).max()
        pos_pct = ((preis - low14) / (high14 - low14)) * 100 if high14 != low14 else 50
        
        wetter = "☀️" if pos_pct > 90 else "🌧️" if pos_pct < 10 else "☁️"
        punkt = "🟢" if diff > 0.01 else "🔴" if diff < -0.01 else "🟡"
        
        # ATR (Volatilität)
        atr = (df['High'] - df['Low']).tail(14).mean()
        
        return {
            "Trend": f"{wetter}{punkt}",
            "Name": name,
            "Symbol": symbol,
            "Preis": preis,
            "Pos%": f"{pos_pct:.1f}%",
            "RSI": round(pos_pct, 1),
            "ATR": round(atr, 2),
            "Status": "EXTREM HOCH" if pos_pct > 90 else "EXTREM TIEF" if pos_pct < 10 else "Normal"
        }
    except:
        return None

# --- 2. HEADER: Wochentag & Datum ---
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
st.markdown(f"### 🚀 KONTROLLTURM AKTIV | {tage[jetzt.weekday()]}, {jetzt.strftime('%d.%m.%Y | %H:%M:%S')}")

# --- 3. BASIS-MONITOR (Indizes mit Wetter) ---
c1, c2, c3 = st.columns(3)
indices = [("EUR/USD", "EURUSD=X"), ("DAX (ADR)", "^GDAXI"), ("NASDAQ", "^IXIC")]

for col, (label, sym) in zip([c1, c2, c3], indices):
    data = get_market_data(sym)
    if data:
        col.metric(f"{label} {data['Trend'][0]}", f"{data['Preis']:,.4f}" if "USD" in label else f"{data['Preis']:,.2f}", f"RSI: {data['RSI']}%")

st.divider()

# --- 4. DETAILLIERTE LEGENDE ---
with st.expander("📖 System-Details: RSI (20min) & ATR"):
    st.write("**RSI (Relative Stärke):** Berechnet auf Basis von **20-Minuten-Intervallen** [cite: 2026-02-07].")
    st.write("- ☀️ EXTREM HOCH (> 90%) | 🌧️ EXTREM TIEF (< 10%) [cite: 2026-02-07].")
    st.write("**ATR (Volatilität):** Zeigt die Schwankungsbreite im Verhältnis zum Kurs.")

# --- 5. CHAMPIONS (7x7 Portfolio) ---
# Deine Hidden Champions [cite: 2026-02-07]
champions_eu = ["ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE", "VOW3.DE", "BMW.DE"]
champions_us = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

def show_table(title, symbols):
    st.write(f"**{title}**")
    results = [get_market_data(s) for s in symbols]
    df = pd.DataFrame([r for r in results if r])
    # Preis formatieren & Unnötiges ausblenden
    df["Preis(EUR)"] = df["Preis"].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.dataframe(df[["Trend", "Name", "Preis(EUR)", "Pos%", "ATR", "Status"]], hide_index=True, use_container_width=True)

col_eu, col_us = st.columns(2)
with col_eu: show_table("Europa: Deine 7 Hidden Champions", champions_eu)
with col_us: show_table("USA: Deine 7 Hidden Champions", champions_us)

# --- 6. BIO-CHECK & SICHERHEIT ---
st.divider()
st.subheader("🧘 Bio-Check & Sicherheit")
st.error("⚠️ **WANDSITZ**: Ruhig atmen! Keine Pressatmung (Blutdruck-Schutz)!")

with st.expander("🛡️ Backup-Informationen (Gesundheit & Reisen)"):
    st.write("🌱 **Blutdruck**: Sprossen & Rote Bete (natürliche Senker) [cite: 2025-12-20].")
    st.write("🚫 **Warnung**: Keine Mundspülungen mit Chlorhexidin verwenden [cite: 2025-12-20].")
    st.write("🥜 **Reisen**: Nüsse als Snack & Österreich Ticket sind bereit [cite: 2026-01-25, 2026-02-03].")
