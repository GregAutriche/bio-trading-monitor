import streamlit as st
import yfinance as yf

# Seite konfigurieren
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. VARIABLE TICKER-LISTE ---
# Hier kannst du jederzeit neue Symbole hinzufügen oder löschen
meine_ticker = {
    "EUR/USD": "EURUSD=X",
    "DAX Index": "^GDAXI",
    "NASDAQ 100": "^IXIC",
    "OTP Bank (HU)": "OTP.BU",
    "Sopharma (BG)": "SFA.SO"
}

# --- 2. FUNKTION FÜR VARIABLEN DATENABRUF ---
def hole_daten(symbol):
    try:
        t = yf.Ticker(symbol)
        # Versuch, 1m-Daten für exakte Uhrzeit zu laden
        df = t.history(period="1d", interval="1m")
        if df.empty:
            df = t.history(period="1d")
        
        if not df.empty:
            kurs = df['Close'].iloc[-1]
            zeit = df.index[-1].strftime('%d.%m. %H:%M')
            return kurs, zeit
        return None, "Keine Daten"
    except:
        return None, "Fehler"

# --- 3. DYNAMISCHE ANZEIGE DER WERTE ---
st.title("📊 Dein Trading- & Bio-Monitor")

# Wir erstellen automatisch so viele Spalten, wie Ticker in der Liste sind
cols = st.columns(len(meine_ticker))

for i, (name, symbol) in enumerate(meine_ticker.items()):
    preis, zeitpunkt = hole_daten(symbol)
    
    # Formatierung je nach Wert (Währung vs. Index)
    format_str = "{:.4f}" if "USD" in name else "{:,.2f}"
    
    cols[i].metric(
        label=name, 
        value=format_str.format(preis) if preis else "Markt zu",
        help=f"Letzter Tick: {zeitpunkt}"
    )

st.caption(f"Letzte Aktualisierung der variablen Liste: {datetime.now().strftime('%H:%M:%S')} Uhr")
st.divider()

# --- 4. CHINA-EXPOSURE LOGIK (10/90 REGEL) ---
st.subheader("📈 Markt-Check & China-Exposure Logik")
# Der 'Fünfer' (05%) aus deinem Screenshot
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

l, m, r = st.columns(3)
with l:
    if wert < 10:
        st.error(f"🔴 **EXTREM TIEF**\n\nBereich: < 10%\n\nStatus: AKTIV")
    else:
        st.info("⚪ Extrem Tief (< 10%)")
with m:
    if 10 <= wert <= 90:
        st.success(f"🟢 **NORMALBEREICH**\n\nBereich: 10% - 90%")
    else:
        st.info("⚪ Normalbereich (10% - 90%)")
with r:
    if wert > 90:
        st.error(f"🔴 **EXTREM HOCH**\n\nBereich: > 90%")
    else:
        st.info("⚪ Extrem Hoch (> 90%)")

st.divider()

# --- 5. BACKUP-INFOS IN EXPANDERN ---
with st.expander("🧘 Gesundheit & Routine"):
    st.write("### Routine: WANDSITZ")
    st.info("⏱️ Dauer: 05 bis 08 Minuten")
    st.warning("⚠️ Atem-Check: Gleichmäßig atmen, keine Preßatmung!")

with st.expander("✈️ Reisen & Ernährung"):
    st.write(f"🎫 **Ticket:** Österreich Ticket vorhanden")
    st.write("🥗 **Ernährung:** Fokus auf Sprossen und Rote Bete")
