}%")

with w2:
    st.success("🟢 Normalbereich (10% - 90%)")
    if not normalbereich: st.markdown(no_data_red, unsafe_allow_html=True)
    for t, v in normalbereich: st.write(f"{t}: {v:.2f}%")

with w3:
    st.warning("🟣 Extrem Hoch (RSI > 90%)")
    if not extrem_hoch: st.markdown(no_data_red, unsafe_allow_html=True)
    for t, v in extrem_hoch: st.write(f"⚠️ **{t}**: {v:.2f}%")

st.divider()

# --- 7. BIO-CHECK ---
st.subheader("🧘 Dein Bio-Check")
b1, b2 = st.columns([1, 1])

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    # Warnung Wandsitz
    st.error("ACHTUNG: Atmen! Keine Pressatmung während des isometrischen Trainings!")

with b2:
    with st.expander("✈️ Reisen & Gesundheit"):
        # Backup-Informationen
        st.write("🥜 Nüsse einplanen (Snack für Reisen)")
        st.write("🌱 Sprossen / Rote Bete (Blutdrucksenkung)")
        st.write("⚠️ Keine Mundspülungen (Chlorhexidin) / Keine Phosphate")

time.sleep(60)
st.rerun()
