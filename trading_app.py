import streamlit as st
import yfinance as yf

# Seite konfigurieren
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. SICHERER DATENABRUF ---
def get_safe_price(ticker_symbol):
    try:
        data = yf.Ticker(ticker_symbol).history(period="5d")
        return data['Close'].iloc[-1] if not data.empty else 0.0
    except:
        return 0.0

# Daten abrufen (Fakten)
eur_usd = get_safe_price("EURUSD=X")
dax_idx = get_safe_price("^GDAXI")
nasdaq_idx = get_safe_price("^IXIC")
# Ticker-Symbole für Ungarn/Bulgarien aus deinen Präferenzen (z.B. OTP Bank)
otp_hu = get_safe_price("OTP.BU") 

# --- 2. TRADING METRIKEN ---
st.title("📊 Dein Trading- & Bio-Monitor")

c1, c2, c3, c4 = st.columns(4)
c1.metric("EUR/USD", f"{eur_usd:.4f}" if eur_usd > 0 else "Markt zu")
c2.metric("DAX Index", f"{dax_idx:,.2f} pkt" if dax_idx > 0 else "Markt zu")
c3.metric("NASDAQ 100", f"{nasdaq_idx:,.2f}" if nasdaq_idx > 0 else "Markt zu")
c4.metric("OTP Bank (HU)", f"{otp_hu:,.0f} HUF" if otp_hu > 0 else "Markt zu")

st.divider()

# --- 3. CHINA-EXPOSURE LOGIK (DEINE REGELN) ---
st.subheader("📈 Markt-Check & China-Exposure")
# Slider zur Simulation der 10%/90% Regel
exp_val = st.slider("Aktueller Wert (%)", 0, 100, 5)

if exp_val < 10:
    st.error(f"Status: **Extrem Tief** ({exp_val}%)") #
elif exp_val > 90:
    st.error(f"Status: **Extrem Hoch** ({exp_val}%)") #
else:
    st.success(f"Status: **Normalbereich** ({exp_val}%)") #

st.divider()

# --- 4. AUFKLAPPBARE INFORMATIONEN (DEIN WUNSCH) ---

with st.expander("🧘 Tägliche Gesundheit & Routine"):
    st.write("### WANDSITZ (Isometrisches Training)") #
    st.info("⏱️ Dauer: **05** bis **08** Minuten")
    st.warning("**Warnung:** Keine Preßatmung! Gleichmäßig atmen.") #
    st.write("* **Vermeiden:** Mundspülungen (Chlorhexidin), Kaugummi nach dem Essen.") #

with st.expander("✈️ Reise-Informationen"):
    st.write("### Unterwegs mit dem Österreich Ticket") #
    st.write("* **Snacks:** Immer Nüsse dabei haben.") #
    st.write("* **Status:** Österreich Ticket ist aktiv.") #

with st.expander("🥗 Ernährung & Blutdruck"):
    st.write("### Blutdrucksenkung") #
    st.write("* **Fokus:** Sprossen und Rote Bete.") #
    st.write("* **Vorsicht:** Phosphate in Fertiggerichten & Grapefruit bei Medikamenten.") #

with st.expander("🆕 Neues & Zusammenfassung"):
    st.write("### Letzte 7 Tage")
    st.write("Hier wird deine wöchentliche Übersicht erscheinen.") #
