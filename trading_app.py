import streamlit as st
import yfinance as yf
from datetime import datetime

# --- 1. START-ZEILE ---
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
heute_name = tage[jetzt.weekday()]
st.markdown(f"## Start: {heute_name}, {jetzt.strftime('%Y %m %d %H:%M:%S')}")
st.divider()

# --- 2. MARKT-CHECK (PRÄZISE FORMATIERUNG) ---
st.subheader("💹 Markt-Check")

def get_format_data(symbol, decimals=2):
    try:
        t = yf.Ticker(symbol)
        d = t.history(period="1d")
        if not d.empty:
            val = d['Close'].iloc[-1]
            # Formatiert mit Tausender-Punkt und Komma
            return f"{val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return "N/A"
    except: return "Error"

c1, c2, c3 = st.columns(3)
with c1: st.metric("Euro/USD", get_format_data("EURUSD=X", 4)) # 4 Stellen wie vereinbart
with c2: st.metric("DAX", get_format_data("^GDAXI", 2))
with c3: st.metric("Nasdaq", get_format_data("^IXIC", 2))

st.divider()

# --- 3. DIE 14 AKTIEN (RECHTSBÜNDIG & EINHEITLICH) ---
st.subheader("🇪🇺 7x Europa & 🇺🇸 7x USA")

europa = ["OTP.BU", "MOL.BU", "ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE"]
usa = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

col_eu, col_us = st.columns(2)

def show_aligned_list(title, tickers):
    st.markdown(f"**{title}**")
    for t in tickers:
        preis = get_format_data(t, 2)
        # HTML/CSS für rechtsbündige Ausrichtung der Zahlen
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; font-family: monospace; max-width: 300px;">
                <span>{t}</span>
                <span>{preis}</span>
            </div>
            """, unsafe_allow_html=True)

with col_eu: show_aligned_list("Europa Portfolio", europa)
with col_us: show_aligned_list("USA Portfolio", usa)

st.divider()

# --- 4. BIO-CHECK & BACKUP ---
st.subheader("🧘 Bio-Check & Sicherheit")
st.error("⚠️ WANDSITZ: Atmen! Keine Pressatmung (Blutdruck)! [cite: 2025-12-20]")
with st.expander("🛡️ Backup-Infos"):
    st.write("🌱 **Blutdruck**: Sprossen & Rote Bete [cite: 2025-12-20]")
    st.write("🥜 **Reise**: Nüsse & Österreich Ticket [cite: 2026-02-03, 2026-01-25]")
