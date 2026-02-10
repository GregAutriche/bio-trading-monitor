import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# Seite konfigurieren
st.set_page_config(page_title="Trading Monitor", layout="wide")

# --- LIVE DATUM & UHRZEIT ---
# Zeigt Datum, Wochentag und Uhrzeit direkt oben an
jetzt = datetime.now()
wochentag_de = {
    "Monday": "Montag", "Tuesday": "Dienstag", "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag", "Friday": "Freitag", "Saturday": "Samstag", "Sunday": "Sonntag"
}
tag_name = wochentag_de.get(jetzt.strftime("%A"), jetzt.strftime("%A"))

st.title("📊 Dein Premium Trading Monitor")
st.markdown(f"### 🕒 {tag_name}, {jetzt.strftime('%d.%m.%Y')} | {jetzt.strftime('%H:%M:%S')} Uhr")

# --- FINANZDATEN ABFRAGE ---
tickers = {
    "EUR/USD": "EURUSD=X",
    "DAX": "^GDAXI",
    "NASDAQ 100": "^NDX",
    "S&P 1000": "^SP1000"
}

def get_data():
    results = []
    for name, symbol in tickers.items():
        try:
            t = yf.Ticker(symbol)
            # Wir nutzen '1d' Intervall für den aktuellsten Preis
            h = t.history(period="5d") 
            if not h.empty:
                current = h['Close'].iloc[-1]
                low_52w = t.history(period="1y")['Low'].min()
                high_52w = t.history(period="1y")['High'].max()
                
                # 10/90 Regel Logik [cite: 2026-02-07]
                pos = ((current - low_52w) / (high_52w - low_52w)) * 100
                if pos > 90: status = "🔴 EXTREM HOCH"
                elif pos < 10: status = "🟢 EXTREM TIEF"
                else: status = "⚪ Normalbereich"
                
                # Dollar auf 8 Stellen, Indizes auf 2
                val = f"{current:.8f}" if "USD" in name else f"{current:,.2f}"
                results.append({"Asset": name, "Kurs": val, "Markt-Bereich": status})
        except Exception:
            results.append({"Asset": name, "Kurs": "Ladefehler", "Markt-Bereich": "-"})
    return pd.DataFrame(results)

# Tabelle anzeigen
st.table(get_data())

# Automatisches Neuladen alle 60 Sekunden für die Aktualisierung
time.sleep(60)
st.rerun()
