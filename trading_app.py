import streamlit as st
import yfinance as yf
import pandas as pd

# Seite konfigurieren
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. FUNKTION FÜR DATENABRUF ---
def get_safe_price(ticker_symbol):
    try:
        data = yf.Ticker(ticker_symbol).history(period="5d")
        if not data.empty:
            return data['Close'].iloc[-1]
        return 0.0
    except:
        return 0.0

# Daten abrufen
eurusd = get_safe_price("EURUSD=X")
dax = get_safe_price("^GDAXI")
nasdaq = get_safe_price("^IXIC")
otp = get_safe_price("OTP.BU")

# --- 2. DASHBOARD LAYOUT ---
st.title("📊 Trading & Bio-Monitor")

# Kurs-Metriken in einer schönen Reihe
col1, col2, col3, col4 = st.columns(4)
col1.metric("EUR/USD", f"{eurusd:.4f}" if eurusd > 0 else "Markt zu")
col2.metric("DAX Index", f"{dax:,.2f} pkt" if dax > 0 else "Markt zu")
col3.metric("NASDAQ 100", f"{nasdaq:,.2f}" if nasdaq > 0 else "Markt zu")
col4.metric("OTP Bank (HU)", f"{otp:,.0f} HUF" if otp > 0 else "Markt zu")

st.markdown("---")

# --- 3. GESUNDHEIT & ROUTINE (WANDSITZ) ---
st.subheader("🧘 Tägliche Gesundheits-Routine")

# Backup-Informationen & Fortschritt
c1, c2 = st.columns([1, 2])
with c1:
    st.info("⏱️ **WANDSITZ**\n\nDauer: **05** bis **08** Min.")
with c2:
    st.warning("**Sicherheitshinweise:**\n\n* Gleichmäßig atmen (Keine Preßatmung!).\n* Kein Chlorhexidin (Mundspülung).\n* Vorsicht bei Phosphaten & Grapefruit.")

st.markdown("---")

# --- 4. CHINA-EXPOSURE & MARKT-STATUS ---
st.subheader("📈 Markt-Check & China-Exposure")

# Schieberegler zum Testen oder Live-Wert
exposure = st.slider("Aktuelles China-Exposure (%)", 0, 100, 5)

if exposure < 10:
    st.error(f"Status: **Extrem Tief** ({exposure}%) - Unter Normalbereich")
elif exposure > 90:
    st.error(f"Status: **Extrem Hoch** ({exposure}%) - Über Normalbereich")
else:
    st.success(f"Status: **Normalbereich** ({exposure}%)")

# --- 5. REISE- & INFO-BACKUP ---
with st.expander("✈️ Reise-Informationen & Ernährung"):
    st.write(f"* **Ticket:** Österreich Ticket vorhanden.")
    st.write(f"* **Ernährung:** Fokus auf Sprossen & Rote Bete.")
    st.write(f"* **Reisen:** Nüsse als Snack einplanen.")
