# --- 7. DYNAMISCHES BACKTESTING (Einzeiler-Design) ---
st.markdown("---")
top_res = None
if st.session_state.scan_active and 'results' in locals() and results:
    valid_hits = [r for r in results if r['signal'] != "Wait"]
    if valid_hits: 
        top_res = sorted(valid_hits, key=lambda x: -x['prob'])[0]

with st.expander(f"📈 Analyse: {top_res['name'] if top_res else '---'}", expanded=True):
    if top_res:
        # Alles in eine Zeile mit Flexbox
        st.markdown(f"""
            <div style='display: flex; align-items: center; gap: 20px; white-space: nowrap;'>
                <!-- 1. Signal -->
                <div style='font-size: 1.2rem; min-width: 45px; text-align: center;' 
                     class='{"sig-box-high" if top_res["prob"] >= 60 else ("sig-box-c" if top_res["signal"]=="C" else "sig-box-p")}'>
                    {top_res['signal']}
                </div>
                <!-- 2. Name & Ticker -->
                <div style='font-size: 0.9rem; color: #aaa; overflow: hidden; text-overflow: ellipsis;'>
                    {top_res['name']} ({top_res['ticker']})
                </div>
                <!-- 3. Kurs -->
                <div style='font-size: 1.8rem; font-weight: bold;'>
                    {top_res['price']:.2f}
                </div>
                <!-- 4. Stop Loss -->
                <div style='font-size: 0.9rem; color: #ff4b4b; margin-top: 5px;'>
                    SL ({top_res['stop']:.2f})
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        
        # Metriken (darunter, um die Lesbarkeit der Zahlen zu erhalten)
        c1, c2, c3 = st.columns(3)
        c1.metric("Wahrscheinlichkeit", f"{top_res['prob']:.1f}%")
        c2.metric("ADX", f"{top_res['adx']:.1f}")
        c3.metric("RSI", f"{top_res['rsi']:.1f}")
        
    else:
        st.info("Bitte starte den Scan oben.")
