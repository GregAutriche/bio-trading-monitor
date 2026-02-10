import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="Sitzungs-Monitor", layout="wide")

# --- INITIALISIERUNG DES START-WERTS (SESSION STATE) ---
if 'start_daten' not in st.session_state:
    st.session_state['start_daten'] = {}
    st.session_state['start_zeit'] = datetime.now().strftime('%H:%M:%S')

# --- HEADER ---
jetzt = datetime.now()
st.markdown(f"## 🕒 {jetzt.strftime('%d.%m.%Y | %H:%M:%S')} Uhr")
st.info(f"Sitzung gestartet um: {st.session_state['start_zeit']}")

tickers = {
    "EUR/USD": "EURUSD=X", 
    "DAX": "^GDAXI", 
    "S&P 1000": "^SP1000"
}

def get_live_data():
    res = {}
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            df = t.history(period="1d") # Nur heutige Daten
            if not df.empty:
                curr = df['Close'].iloc[-1]
                
                # Speichere den ALLERERSTEN Wert dieser Sitzung
                if name not in st.session_state['start_daten']:
                    st.session_state['start_daten'][name] = curr
                
                start_val = st.session_state['start_daten'][name]
                diff = curr - start_val
                diff_pct = (diff / start_val) * 100 if start_val != 0 else 0
                
                # 10/90 Logik für Wetter & Farbe [cite: 2026-02-07]
                hist = t.history(period="1y")
                low, high = hist['Low'].min(), hist['High'].max()
                pos = ((curr - low) / (high - low)) * 100
                
                if pos > 90: icon, color = "☀️", "red"
                elif pos < 10: icon, color = "⛈️", "green"
                else: icon, color = "⛅", "orange"
                
                res[name] = {
                    "kurs": f"{curr:.8f}" if "USD" in name else f"{curr:,.2f}",
                    "start": f"{start_val:.8f}" if "USD" in name else f"{start_val:,.2f}",
                    "icon": icon, "color": color, "diff": diff, "diff_pct": diff_pct
                }
        except: continue
    return res

data = get_live_data()

# --- ANZEIGE OBEN: LIVE-KURSE ---
cols = st.columns(len(data))
for i, (name, d) in enumerate(data.items()):
    with cols[i]:
        st.markdown(f"### {d['icon']} {name}")
        st.markdown(f"<h2 style='color:{d['color']};'>{d['kurs']}</h2>", unsafe_allow_html=True)
        # Live-Differenz zur Sitzung
        color_diff = "green" if d['diff'] >= 0 else "red"
        st.markdown(f"Seit Start: <b style='color:{color_diff};'>{d['diff']:+.4f} ({d['diff_pct']:+.2f}%)</b>", unsafe_allow_html=True)

st.divider()

# --- SLIDER FÜR DETAILS & DOKUMENTATION ---
with st.expander("📊 Sitzungs-Dokumentation (Live-Werte)"):
    doc_df = pd.DataFrame([
        {"Asset": k, "Start-Kurs": v["start"], "Aktuell": v["kurs"], "Änderung": f"{v['diff_pct']:+.2f}%"} 
        for k, v in data.items()
    ])
    st.table(doc_df)
    if st.button("Sitzungswerte zurücksetzen"):
        st.session_state.clear()
        st.rerun()

# Automatischer Refresh für die Live-Interpretation
time.sleep(2)
st.rerun()



