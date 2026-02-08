import streamlit as st
import yfinance as yf
from datetime import datetime

# --- 1. START-ZEILE ---
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
st.markdown(f"## Start: {tage[jetzt.weekday()]}, {jetzt.strftime('%Y %m %d %H:%M:%S')}")
st.divider()

# --- 2. MARKT-CHECK ---
def get_market_data(symbol, decimals=2):
    try:
        t = yf.Ticker(symbol)
        d = t.history(period="14d")
        # Namen abrufen (Neu)
        name = t.info.get('shortName', symbol) 
        if not d.empty:
            val = d['Close'].iloc[-1]
            prev = d['Close'].iloc[-2]
            diff = ((val - prev) / prev) * 100
            low14, high14 = d['Close'].min(), d['Close'].max()
            score = ((val - low14) / (high14 - low14)) * 100 if high14 != low14 else 50
            wetter = "☀️" if score > 90 else "🌧️" if score < 10 else "☁️"
            fmt = f"{val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return fmt, diff, wetter, name
        return "N/A", 0, "❓", symbol
    except: return "N/A", 0, "❓", symbol

st.subheader("💹 Markt-Check & Börsen-Wetter")
c1, c2, c3 = st.columns(3)
for col, (lbl, sym, dec) in zip([c1, c2, c3], [("Euro/USD", "EURUSD=X", 4), ("DAX", "^GDAXI", 2), ("Nasdaq", "^IXIC", 2)]):
    val, _, wet, _ = get_market_data(sym, dec)
    col.metric(f"{lbl} {wet}", val)
st.divider()

# --- 3. DIE 14 AKTIEN MIT NAMEN ---
st.subheader("🇪🇺 7x Europa & 🇺🇸 7x USA")
with st.expander("📖 Legende: Farben & Symbole"):
    st.write("☀️/☁️/🌧️ = Wetter (RSI) | 🟢/🔴/🟡 = Kurs-Trend")

europa = ["OTP.BU", "MOL.BU", "ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE"]
usa = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

def show_aligned_list(title, tickers):
    st.markdown(f"**{title}**")
    for t in tickers:
        preis, diff, wetter, name = get_market_data(t, 2)
        farbe = "#28a745" if diff > 0.01 else "#dc3545" if diff < -0.01 else "#ffc107"
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; font-family: sans-serif; border-bottom: 1px solid #f0f2f6; padding: 3px 0;">
                <span style="font-size: 0.9rem;">{wetter} {name}</span>
                <span style="color: {farbe}; font-weight: bold; font-family: monospace;">{preis}</span>
            </div>
            """, unsafe_allow_html=True)

col_eu, col_us = st.columns(2)
with col_eu: show_aligned_list("Europa Portfolio", europa)
with col_us: show_aligned_list("USA Portfolio", usa)
st.divider()

# --- 4. BIO-CHECK & SICHERHEIT ---
st.subheader("🧘 Bio-Check & Sicherheit")
st.error("⚠️ WANDSITZ: Atmen! Keine Pressatmung (Blutdruck)! [cite: 2025-12-20]")
with st.expander("🛡️ Backup-Informationen"):
    st.write("🌱 **Blutdruck**: Sprossen & Rote Bete [cite: 2025-12-20]")
    st.write("🥜 **Reise**: Nüsse & Österreich Ticket [cite: 2026-02-03, 2026-01-25]")
