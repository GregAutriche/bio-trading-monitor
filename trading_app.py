import streamlit as st
import yfinance as yf

# Seite konfigurieren
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. FUNKTION FÜR DATENABRUF ---
def get_live_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # Wir schauen nur auf heute. Wenn leer, geben wir None zurück.
        df = ticker.history(period="1d")
        if not df.empty:
            return df['Close'].iloc[-1]
        return None
    except:
        return None

# Daten abrufen
eurusd = get_live_data("EURUSD=X")
dax = get_live_data("^GDAXI")
nasdaq = get_live_data("^IXIC")

# --- 2. HEADER & METRIKEN ---
st.title("📊 Dein Trading- & Bio-Monitor")

c1, c2, c3 = st.columns(3)
# Wenn kein Wert da ist, zeigen wir "Markt geschlossen"
c1.metric("EUR/USD", f"{eurusd:.4f}" if eurusd else "Markt geschlossen")
c2.metric("DAX Index", f"{dax:,.2f} pkt" if dax else "Markt geschlossen")
c3.metric("NASDAQ 100", f"{nasdaq:,.2f}" if nasdaq else "Markt geschlossen")

st.divider()

# --- 3. CHINA-EXPOSURE & LOGIK-DARSTELLUNG ---
st.subheader("📈 Markt-Check & China-Exposure")

# Simulation eines Wertes (z.B. durch deine DAX-Berechnung)
# Wenn wir am Wochenende sind, setzen wir 'aktueller_wert' auf None
aktueller_wert = dax if dax else None 

# FALL A: KEIN WERT DA (Zeige gesamte Logik)
if aktueller_wert is None:
    st.info("ℹ️ Keine Live-Daten verfügbar. Hier ist die geltende Bewertungslogik:")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.error("🔴 **Extrem Tief**\n\nBereich: < 10%")
    with col_b:
        st.success("🟢 **Normalbereich**\n\nBereich: 10% - 90%")
    with col_c:
        st.error("🔴 **Extrem Hoch**\n\nBereich: > 90%")

# FALL B: WERT IST DA (Zeige spezifische Analyse)
else:
    # Beispielhafte Berechnung des Exposure-Status (hier 5% als Beispiel)
    exposure_beispiel = 5 
    st.write(f"Aktueller Live-Status: **{exposure_beispiel:02d}%**")
    
    if exposure_beispiel < 10:
        st.error(f"🚨 Status: **Extrem Tief** (< 10%)")
    elif exposure_beispiel > 90:
        st.error(f"🚀 Status: **Extrem Hoch** (> 90%)")
    else:
        st.success(f"✅ Status: **Normalbereich**")

st.divider()

# --- 4. AUFKLAPPBARE INFORMATIONEN (PROFIL-DATEN) ---

with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Dauer: **05** bis **08** Minuten")
    st.warning("⚠️ **Wichtig:** Keine Preßatmung! Gleichmäßig atmen zur Blutdrucksenkung.")
    st.write("* **Mundhygiene:** Kein Chlorhexidin verwenden.")
    st.write("* **Timing:** Nicht unmittelbar nach dem Essen Zähne putzen.")

with st.expander("✈️ Reisen & Ernährung"):
    st.write("### Reise-Informationen")
    st.write(f"* **Ticket:** Österreich-Ticket vorhanden.")
    st.write("* **Snacks:** Nüsse einplanen.")
    st.write("### Ernährung")
    st.write("* **Blutdruck:** Fokus auf Sprossen und Rote Bete.")
    st.write("* **Vermeiden:** Phosphate in Fertiggerichten.")

with st.expander("🆕 Letzte 7 Tage Übersicht"):
    st.write("### Zusammenfassung")
    st.write("Übersicht über die Fortschritte beim Wandsitz und die Marktbewegungen.")
