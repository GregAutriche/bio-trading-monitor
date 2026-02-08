import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# SEITEN-KONFIGURATION
st.set_page_config(page_title="Kontrollturm Live", layout="wide")

# --- 1. DATEN-LOGIK (RSI & ROC) ---
def get_market_data(symbol):
    try:
        t = yf.Ticker(symbol)
        # 15m Daten für präzise 20-Minuten-RSI & ROC Annäherung [cite: 2026-02-07]
        df = t.history(period="5d", interval="15m")
        if df.empty or len(df) < 15: 
            df = t.history(period="20d")
        
        preis = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        diff_heute = ((preis - prev) / prev) * 100
        
        # RSI / Position Logik (14 Intervalle) [cite: 2026-02-07]
        low14, high14 = df['Close'].tail(14).min(), df['Close'].tail(14).max()
        pos_pct = ((preis - low14) / (high14 - low14)) * 100 if high14 != low14 else 50
        
        # ROC Logik (Rate of Change über 14 Intervalle) [cite: 2026-02-07]
        past_price = df['Close'].iloc[-14]
        roc_val = ((preis - past_price) / past_price) * 100
        
        # Symbole
        wetter = "☀️" if pos_pct > 90 else "🌧️" if pos_pct < 10 else "☁️"
        punkt = "🟢" if diff_heute > 0.01 else "🔴" if diff_heute < -0.01 else "🟡"
        
        atr = (df['High'] - df['Low']).tail(14).mean()
        
        return {
            "Preis": preis, "Trend": f"{wetter}{punkt}", "Wetter": wetter,
            "RSI": round(pos_pct, 1), "ROC": round(roc_val, 2), "ATR": round(atr, 2),
            "Name": t.info.get('shortName', symbol), "Symbol": symbol
        }
    except: return None

# --- 2. HEADER: Wochentag & Datum ---
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
st.markdown(f"### 🚀 KONTROLLTURM AKTIV | {tage[jetzt.weekday()]}, {jetzt.strftime('%d.%m.%Y | %H:%M:%S')}")

# --- 3. BASIS-MONITOR (Mit RSI & ROC) ---
c1, c2, c3 = st.columns(3)
indices = [("EUR/USD", "EURUSD=X"), ("DAX (ADR)", "^GDAXI"), ("NASDAQ", "^IXIC")]

for col, (label, sym) in zip([c1, c2, c3], indices):
    d = get_market_data(sym)
    if d:
        col.metric(
            f"{label} {d['Trend']}", 
            f"{d['Preis']:,.4f}" if "USD" in label else f"{d['Preis']:,.2f}", 
            f"RSI: {d['RSI']}% | ROC: {d['ROC']}%"
        )

st.divider()

# --- 4. DETAILLIERTE LEGENDE ---
with st.expander("📖 System-Details: RSI, ROC & Symbole"):
    st.write("### 🌦️ Wetter (RSI - Position)")
    st.write("- ☀️ **Sonne**: Überkauft (> 90%). Markt ist 'heiß' [cite: 2026-02-07].")
    st.write("- 🌧️ **Regen**: Überverkauft (< 10%). Markt ist 'kalt' [cite: 2026-02-07].")
    st.write("### 🚀 Dynamik (ROC - Geschwindigkeit)")
    st.write("- **ROC**: Zeigt die prozentuale Beschleunigung über 14 Intervalle (20-Min-Basis) [cite: 2026-02-07].")
    st.write("### 🟢🔴 Trend (Tagesänderung)")
    st.write("- Punktfarbe zeigt die Richtung seit dem letzten Schlusskurs an.")

# --- 5. CHAMPIONS (7x7 Portfolio) ---
champions_eu = ["ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE", "VOW3.DE", "BMW.DE"]
champions_us = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

def show_champs(title, symbols):
    st.write(f"**{title}**")
    data = [get_market_data(s) for s in symbols]
    df = pd.DataFrame([d for d in data if d])
    # Anzeige-Formatierung
    df["Preis(EUR)"] = df["Preis"].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df["Pos%"] = df["RSI"].apply(lambda x: f"{x}%")
    df["Status"] = df["RSI"].apply(lambda x: "EXTREM HOCH" if x > 90 else "EXTREM TIEF" if x < 10 else "Normal")
    st.dataframe(df[["Trend", "Name", "Preis(EUR)", "Pos%", "ROC", "ATR", "Status"]], hide_index=True, use_container_width=True)

ca, cb = st.columns(2)
with ca: show_champs("Europa: Deine 7 Hidden Champions", champions_eu)
with cb: show_champs("USA: Deine 7 Hidden Champions", champions_us)

# --- 6. BIO-CHECK & SICHERHEIT ---
st.divider()
st.error("⚠️ **WANDSITZ**: Ruhig atmen! Keine Pressatmung (Blutdruck-Schutz)!")
with st.expander("🛡️ Backup-Infos (Gesundheit & Reisen)"):
    st.write("🌱 **Blutdruck**: Sprossen & Rote Bete nutzen [cite: 2025-12-20].")
    st.write("🥜 **Reisen**: Nüsse als Snack & Österreich Ticket bereit [cite: 2026-01-25, 2026-02-03].")
    st.write("🚫 **Warnung**: Keine Mundspülungen (Chlorhexidin), kein Zähneputzen direkt nach dem Essen [cite: 2025-12-20].")

