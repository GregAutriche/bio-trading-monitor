import streamlit as st
import yfinance as yf
from datetime import datetime

# --- 1. START-ZEILE ---
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
heute_name = tage[jetzt.weekday()]
st.markdown(f"## Start: {heute_name}, {jetzt.strftime('%Y %m %d %H:%M:%S')}")
st.divider()

# --- 2. MARKT-CHECK FUNKTION (INKL. WETTER/RSI) ---
def get_market_data(symbol, decimals=2):
    try:
        t = yf.Ticker(symbol)
        d = t.history(period="14d") # 14 Tage für RSI-Berechnung
        if not d.empty and len(d) > 1:
            val = d['Close'].iloc[-1]
            prev = d['Close'].iloc[-2]
            diff = ((val - prev) / prev) * 100
            
            # Einfache Wetter-Logik (RSI-Näherung)
            # > 90% Extrem Hoch (Sonne/Warnung), < 10% Extrem Tief (Regen/Chance)
            # Hier nutzen wir die Preis-Position der letzten 14 Tage als Wetter-Indikator
            low14 = d['Close'].min()
            high14 = d['Close'].max()
            wetter_score = ((val - low14) / (high14 - low14)) * 100 if high14 != low14 else 50
            
            wetter = "☀️" if wetter_score > 90 else "🌧️" if wetter_score < 10 else "☁️"
            formatted = f"{val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return formatted, diff, wetter
        return "N/A", 0, "❓"
    except: return "N/A", 0, "❓"

st.subheader("💹 Markt-Check & Börsen-Wetter")
c1, c2, c3 = st.columns(3)
for col, (label, sym, dec) in zip([c1, c2, c3], [("Euro/USD", "EURUSD=X", 4), ("DAX", "^GDAXI", 2), ("Nasdaq", "^IXIC", 2)]):
    val, diff, wetter = get_market_data(sym, dec)
    col.metric(f"{label} {wetter}", val)

st.divider()

# --- 3. DIE 14 AKTIEN (7x EUROPA & 7x USA) ---
# Überschrift jetzt ohne (no data)
st.subheader("🇪🇺 7x Europa & 🇺🇸 7x USA")

europa = ["OTP.BU", "MOL.BU", "ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE"]
usa = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

def show_aligned_list(title, tickers):
    st.markdown(f"**{title}**")
    for t in tickers:
        preis, diff, wetter = get_market_data(t, 2)
        # Farb-Logik wie im Bild 2265e493 bereits erfolgreich umgesetzt
        farbe = "#28a745" if diff > 0.01 else "#dc3545" if diff < -0.01 else "#ffc107"
        
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; font-family: monospace; font-size: 1.1rem; border-bottom: 1px solid #f0f2f6; padding: 2px 0;">
                <span>{wetter} {t}</span>
                <span style="color: {farbe}; font-weight: bold;">{preis}</span>
            </div>
            """, unsafe_allow_html=True)

col_eu, col_us = st.columns(2)
with col_eu: show_aligned_list("Europa Portfolio", europa)
with col_us: show_aligned_list("USA Portfolio", usa)
st.divider()

# --- 4. BIO-CHECK & BACKUP (WIE VEREINBART) ---
st.subheader("🧘 Bio-Check & Sicherheit")
st.error("⚠️ WANDSITZ: Atmen! Keine Pressatmung (Blutdruck)! [cite: 2025-12-20]")
with st.expander("🛡️ Backup-Infos"):
    st.write("🌱 **Blutdruck**: Sprossen & Rote Bete [cite: 2025-12-20]")
    st.write("🥜 **Reise**: Nüsse & Österreich Ticket [cite: 2026-01-25, 2026-02-03]")
