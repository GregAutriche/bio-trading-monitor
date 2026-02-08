import streamlit as st
import yfinance as yf
import pandas as pd

# Seite konfigurieren
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. FUNKTION FÜR SICHEREN DATENABRUF ---
def get_safe_price(ticker_symbol):
    try:
        # Wir rufen 5 Tage ab, um auch am Wochenende den letzten Schlusskurs zu haben
        data = yf.Ticker(ticker_symbol).history(period="5d")
        if not data.empty:
            return data['Close'].iloc[-1]
        return 0.0
    except:
        return 0.0

# Daten abrufen (Fakten)
eurusd = get_safe_price("EURUSD=X")
dax = get_safe_price("^GDAXI")
nasdaq = get_safe_price("^IXIC")
otp = get_safe_price("OTP.BU") # Ungarn Ticker aus deinen Notizen

# --- 2. HEADER & TRADING METRIKEN ---
st.title("📊 Dein Trading- & Bio-Monitor")

col1, col2, col3, col4 = st.columns(4)
col1.metric("EUR/USD", f"{eurusd:.4f}" if eurusd > 0 else "Markt zu")
col2.metric("DAX Index", f"{dax:,.2f} pkt" if dax > 0 else "Markt zu")
col3.metric("NASDAQ 100", f"{nasdaq:,.2f}" if nasdaq > 0 else "Markt zu")
col4.metric("OTP Bank (HU)", f"{otp:,.0f} HUF" if otp > 0 else "Markt zu")

st.divider()

# --- 3. CHINA-EXPOSURE (10%/90% REGEL) ---
st.subheader("📈 Markt-Check & China-Exposure")
exposure = st.slider("Aktuelles China-Exposure im DAX (%)", 0, 100, 5)

if exposure < 10:
    st.error(f"Status: **Extrem Tief** ({exposure}%) - Unter Normalbereich")
elif exposure > 90:
    st.error(f"Status: **Extrem Hoch** ({exposure}%) - Über Normalbereich")
else:
    st.success(f"Status: **Normalbereich** ({exposure}%)")

st.divider()

# --- 4. AUFKLAPPBARE SEKTIONEN (DEIN WUNSCH) ---

# Sektion: Gesundheit & Routine
with st.expander("🧘 Tägliche Gesundheits-Routine & Wandsitz"):
    st.write("### Routine: WANDSITZ")
    st.info("⏱️ **Empfohlene Dauer:** 05 bis 08 Minuten")
    st.warning("**Wichtiger Sicherheits-Check:**")
    st.write("""
    * **Atmung:** Gleichmäßig weiteratmen! Niemals die Luft anhalten (Preßatmung vermeiden).
    * **Vorsicht:** Achte auf Wechselwirkungen mit Blutdrucksenkern (z.B. Grapefruit-Interaktionen).
    * **Tabu:** Keine Mundspülungen mit Chlorhexidin verwenden.
    """)

# Sektion: Reise-Informationen
with st.expander("✈️ Reise-Informationen"):
    st.write("### Unterwegs & Transport")
    st.success("🎫 **Österreich-Ticket:** Vorhanden und aktiv.")
    st.write("""
    * **Vorbereitung:** Bei Reisen immer an die Notfall-Snacks (Nüsse) denken.
    * **Isometrie:** Wandsitz kann oft auch diskret in Hotelzimmern oder an Bahnhöfen durchgeführt werden.
    """)

# Sektion: Ernährung
with st.expander("🥗 Ernährung & Blutdruck-Fokus"):
    st.write("### Blutdrucksenkende Ernährung")
    st.write("""
    * **Superfoods:** Aktiv Sprossen und Rote Bete in den Speiseplan einbauen.
    * **Vermeidung:** Vorsicht bei Phosphaten (oft in Fertiggerichten enthalten).
    * **Timing:** Nach dem Essen nicht sofort Zähne putzen oder Kaugummi kauen.
    """)

# Sektion: Neues & Backup (Wandsitz Info)
with st.expander("📝 Neues & Backup-Informationen"):
    st.write("### Zusammenfassung der letzten 7 Tage")
    st.write("Hier kannst du zukünftig deine täglichen Fortschritte protokollieren.")
    st.info("Erinnerung: Backup-Info 'Wandsitz' etc. ist dauerhaft im System hinterlegt.")
