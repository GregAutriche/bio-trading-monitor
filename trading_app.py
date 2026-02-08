import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# --- KONTROLLTURM KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading-Monitor", layout="wide")

# Akustisches Signal beim Laden/Update (JavaScript)
st.components.v1.html("""
    <script>
    function playBeep() {
        var context = new AudioContext();
        var o = context.createOscillator();
        o.type = 'sine'; o.frequency.setValueAtTime(1000, context.currentTime);
        o.connect(context.destination); o.start();
        setTimeout(function(){ o.stop(); }, 400);
    }
    window.onload = playBeep;
    </script>
""", height=0)

def get_status(pos):
    if pos > 90: return "☀️ EXTREM HOCH"
    if pos < 10: return "⛈️ EXTREM TIEF"
    return "Normal"

# --- DATEN-LOGIK ---
INDICES = ["^GDAXI", "^IXIC"]
CHAMPIONS = ["ASML.AS", "MC.PA", "SU.PA", "SAP.DE", "AAPL", "SYK", "MSFT", "NVDA", "OTP.BD", "PKO.WA"]

@st.cache_data(ttl=15)
def fetch_data():
    usd = yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[-1]
    results = []
    for t in (INDICES + CHAMPIONS):
        s = yf.Ticker(t); h = s.history(period="60d"); h_y = s.history(period="1y")
        curr = h['Close'].iloc[-1]
        pos = ((curr - h_y['Low'].min()) / (h_y['High'].max() - h_y['Low'].min())) * 100
        p_eur = curr if any(x in t for x in [".DE", ".AS", ".PA", ".BD", "^"]) else curr / usd
        results.append({"Symbol": t, "Preis(EUR)": round(p_eur, 2), "Pos%": round(pos, 1), "Status": get_status(pos)})
    return results, usd

data, eur_usd = fetch_data()
df = pd.DataFrame(data)

# --- ANZEIGE (Wie im schwarzen Fenster) ---
st.title("🛰️ KONTROLLTURM LIVE")
st.write(f"**Update:** {datetime.datetime.now().strftime('%H:%M:%S')} | **EUR/USD:** {round(eur_usd, 4)}")

# Markt-Wetter basierend auf DAX
dax_pos = df[df['Symbol'] == '^GDAXI']['Pos%'].values[0]
wetter = "⚠️ Hitzewelle!" if dax_pos > 85 else "⛈️ Gewitter!" if dax_pos < 15 else "🌤️ Heiter"
st.info(f"**MARKT-WETTER:** {wetter}")

# Tabellen abgesetzt
st.subheader("📊 INDIZES")
st.dataframe(df[df['Symbol'].isin(INDICES)])

st.subheader("🏆 HIDDEN CHAMPIONS")
st.dataframe(df[df['Symbol'].isin(CHAMPIONS)])

st.divider()
st.write("🧘 **Routine:** WANDSITZ (90°) & RUHIG ATMEN") [cite: 2026-02-03]
