import streamlit as st

# --- Routine Sektion ---
st.subheader("Tägliche Gesundheits-Routine")

# WICHTIG: Die Zahlen müssen in Anführungszeichen stehen ("08"), 
# damit der "leading zeros" Fehler verschwindet.
st.write("🧘 **Routine:** WANDSITZ")
st.info("⏱️ Empfohlene Dauer: **05 bis 08** Minuten")

# Dein persönlicher Reminder für das Training
st.warning("⚠️ **Wichtiger Hinweis:** Während des Wandsitzes gleichmäßig atmen! Keine Preßatmung (Valsalva-Manöver), um den Blutdruck stabil zu halten.")

# --- Marktanalyse (Beispiel für deine 10%/90% Regel) ---
st.divider()
st.subheader("Markt-Check & China-Exposure")

# Beispielwert für die Anzeige (Hier als Text formatiert)
kurs_status = "05" # Beispiel für einen extrem tiefen Kurs < 10%
st.write(f"Aktueller Status-Wert: **{kurs_status}%**")

if int(kurs_status) < 10:
    st.error("🚨 Status: Extrem Tief (< 10%)")
elif int(kurs_status) > 90:
    st.error("🚀 Status: Extrem Hoch (> 90%)")
else:
    st.success("✅ Status: Normalbereich (10% - 90%)")

