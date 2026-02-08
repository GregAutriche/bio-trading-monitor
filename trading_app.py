import streamlit as st
import yfinance as yf
from datetime import datetime

# --- 1. START-ZEILE ---
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
heute_name = tage[jetzt.weekday()]
st.markdown(f"## Start: {heute_name}, {jetzt.strftime('%Y %m %d %H:%M:%S')}")
st.divider()

# --- 2. MARKT-CHECK FUNKTION ---
def get_format_data(symbol, decimals=2):
    try:
        t = yf.Ticker(symbol)
        # Wir laden 5 Tage, um sicher den letzten Freitag zu finden (wichtig für N/A Titel)
        d = t.history(period="5d")
        if not d.empty:
            val = d['Close'].iloc[-1]
            return f"{val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return "Lädt..."
    except: return "Fehler"

st.subheader("💹 Markt-Check")
c1, c2, c3 = st.columns(3)
with c1: st.metric("Euro/USD", get_format_data("EURUSD=X", 4))
with c2: st.metric("DAX", get_format_data("^GDAXI", 2))
with c3: st.metric("Nasdaq", get_format_data("^IXIC", 2))
st.divider()

# --- 3. DIE 14 AKTIEN (RECHTSBÜNDIG OHNE N/A) ---
st.subheader("🇪🇺 7x Europa & 🇺🇸 7x USA")
europa = ["OTP.BU", "MOL.BU", "ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE"]
usa = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

def show_aligned_list(title, tickers):
    st.markdown(f"**{title}**")
    for t in tickers:
        preis = get_format_data(t, 2)
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; font-family: 'Courier New', monospace; font-size: 1.1rem; border-bottom: 1px solid #f0f2f6; padding: 2px 0;">
                <span>{t}</span>
                <span style="font-weight: bold;">{preis}</span>
            </div>
            """, unsafe_allow_html=True)

col_eu, col_us = st.columns(2)
with col_eu: show_aligned_list("Europa Portfolio", europa)
with col_us: show_aligned_list("USA Portfolio", usa)
st.divider()

# --- 4. BIO-CHECK & SICHERHEIT (WIE VEREINBART) ---
st.subheader("🧘 Bio-Check & Sicherheit")
st.error("⚠️ WANDSITZ: Atmen! Keine Pressatmung (Blutdruck)! [cite: 2025-12-20]")
with st.expander("🛡️ Backup-Infos"):
    st.write("🌱 **Blutdruck**: Sprossen & Rote Bete nutzen [cite: 2025-12-20]")
    st.write("🥜 **Reise**: Nüsse als Snack & Österreich Ticket aktiv [cite: 2026-02-03, 2026-01-25]")
    st.write("🚫 **Hygiene**: Keine Mundspülung (Chlorhexidin) [cite: 2025-12-20]")
