import streamlit as st
import yfinance as yf

# Konfiguration der Seite
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. DATENABRUF (FAKTEN) ---
# Hier rufen wir die Live-Kurse ab
try:
    # Währungen & Indizes
    eurusd = yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[-1]
    dax_index = yf.Ticker("^GDAXI").history(period="1d")['Close'].iloc[-1]
    nasdaq_index = yf.Ticker("^IXIC").history(period="1d")['Close'].iloc[-1]
    
    # Beispiel für ungarische/bulgarische Ticker (wie im Profil hinterlegt)
    # OTP Bank (Ungarn): OTP.BU | Sopharma (Bulgarien): SFA.SO
    otp_bank = yf.Ticker("OTP.BU").history(period="1d")['Close'].iloc[-1]
except Exception as e:
    st.error(f"Fehler beim Abrufen der Marktdaten: {e}")
    eurusd, dax_index, nasdaq_index, otp_bank = 0, 0, 0, 0

# --- 2. HEADER & METRIKEN (VISUALISIERUNG) ---
st.title("Dein Trading-Dashboard")

col1, col2, col3, col4 = st.columns(4)
col1.metric("EUR/USD", f"{eurusd:.5f}")
col2.metric("DAX Index", f"{dax_index:,.2f} pkt")
col3.metric("NASDAQ 100", f"{nasdaq_index:,.2f}")
col4.metric("OTP Bank (HU)", f"{otp_bank:,.0f} HUF")

st.divider()

# --- 3. TÄGLICHE GESUNDHEITS-ROUTINE (WANDSITZ) ---
# Backup-Info: Wandsitz zur Blutdrucksenkung
st.subheader("Tägliche Gesundheits-Routine")

# Der Fix für den SyntaxError: Zahlen als Strings "05" / "08"
st.write("🧘 **Routine:** WANDSITZ")
st.info("⏱️ Empfohlene Dauer: **05** bis **08** Minuten")

# Wichtige Warnhinweise aus deinem Profil
st.warning("""
**Wichtige Sicherheitsregeln:**
* Keine Preßatmung beim Wandsitz (immer gleichmäßig atmen)!
* Keine Mundspülungen mit Chlorhexidin verwenden.
* Vorsicht bei Phosphaten in Fertiggerichten.
""")

st.divider()

# --- 4. MARKT-CHECK & CHINA-EXPOSURE ---
st.subheader("Markt-Check & China-Exposure")

# Statische Fundamentaldaten kombiniert mit Live-Kursen
# Hier definieren wir den Wert für die 10%/90% Regel
exposure_wert = 5  # Beispielwert in Prozent

st.write(f"Aktueller China-Exposure-Wert: **{exposure_wert:02d}%**")

if exposure_wert < 10:
    st.error("🚨 Status: Extrem Tief (< 10%)") #
elif exposure_wert > 90:
    st.error("🚀 Status: Extrem Hoch (> 90%)") #
else:
    st.success("✅ Status: Normalbereich (10% - 90%)") #

# --- ZUSÄTZLICHE INFOS ---
with st.expander("Weitere Informationen (Reisen & Ernährung)"):
    st.write("* **Reisen:** Nüsse einpacken!")
    st.write("* **Transport:** Österreich-Ticket ist vorhanden.")
    st.write("* **Er Ernährung:** Fokus auf Sprossen und Rote Bete zur Blutdrucksenkung.")
