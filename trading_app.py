import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# SEITEN-KONFIGURATION
st.set_page_config(page_title="Kontrollturm Live", layout="wide")

# --- 1. DATEN-LOGIK ---
def get_market_data(symbol, is_index=False):
    try:
        t = yf.Ticker(symbol)
        # 15m Daten für die 20-Minuten-RSI Annäherung [cite: 2026-02-07]
        df = t.history(period="5d", interval="15m")
        if df.empty: df = t.history(period="20d")
        
        preis = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        diff = ((preis - prev) / prev) * 100
        
        # RSI / Position Logik [cite: 2026-02-07]
        low14, high14 = df['Close'].tail(14).min(), df['Close'].tail(14).max()
        pos_pct = ((preis - low14) / (high14 - low14)) * 100 if high14 != low14 else 50
        
        # Wetter (Position) & Punkt (Trend)
        wetter = "☀️" if pos_pct > 90 else "🌧️" if pos_pct < 10 else "☁️"
        punkt = "🟢" if diff > 0.01 else "🔴" if diff < -0.01 else "🟡"
        
        atr = (df['High'] - df['Low']).tail(14).mean()
        
        return {
            "Preis": preis, "Trend": f"{wetter}{punkt}", "Wetter": wetter,
            "RSI": round(pos_pct, 1), "ATR": round(atr, 2), "Diff": diff,
            "Name": t.info.get('shortName', symbol)
        }
    except: return None

# --- 2. HEADER: Wochentag & Datum ---
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
st.markdown(f"### 🚀 KONTROLLTURM AKTIV | {tage[jetzt.weekday()]}, {jetzt.strftime('%d.%m.%Y | %H:%M:%S')}")

# --- 3. BASIS-MONITOR (Oben) ---
c1, c2, c3 = st.columns(3)
indices = [("EUR/USD", "EURUSD=X"), ("DAX (ADR)", "^GDAXI"), ("NASDAQ", "^IXIC")]

for col, (label, sym) in zip([c1, c2, c3], indices):
    d = get_market_data(sym)
    if d:
        # Wetterzeichen oben jetzt identisch zur Tabelle
        col.metric(f"{label} {d['Wetter']}", f"{d['Preis']:,.4f}" if "USD" in label else f"{d['Preis']:,.2f}", f"RSI: {d['RSI']}%")

st.divider()

# --- 4. DETAILLIERTE LEGENDE (ERKLÄRUNG FARBEN & WETTER) ---
with st.expander("📖 Detaillierte Legende: Was bedeuten die Symbole?"):
    st.write("### 🌦️ Das Börsen-Wetter (RSI auf 20-Minuten-Basis)")
    st.write("- ☀️ **Sonne**: Kurs extrem hoch (> 90%). Überhitzt, Vorsicht vor Rücksetzern [cite: 2026-02-07].")
    st.write("- ☁️ **Wolke**: Normalbereich (10% - 90%). Stabiler Kursverlauf [cite: 2026-02-07].")
    st.write("- 🌧️ **Regen**: Kurs extrem tief (< 10%). Ausverkauft, potenzielle Kaufzone [cite: 2026-02-07].")
    
    st.divider()
    
    st.write("### 🟢🔴 Der Trend-Punkt (Tagesbewegung)")
    st.write("- 🟢 **Grüner Punkt**: Kurs steigt aktuell (> 0.01% zum Vortag).")
    st.write("- 🟡 **Gelber Punkt**: Kurs ist neutral / stabil.")
    st.write("- 🔴 **Roter Punkt**: Kurs fällt aktuell (< -0.01% zum Vortag).")
    
    st.divider()
    
    st.write("### 📉 Volatilität & Herkunft")
    st.write("- **ATR**: Durchschnittliche Schwankung pro Intervall im Verhältnis zum Preis.")
    st.write("- **Daten**: Live-Feed via Yahoo Finance API [cite: 2025-12-24].")

# --- 5. CHAMPIONS (7x7 Portfolio) ---
# Deine Hidden Champions [cite: 2026-02-07]
champions_eu = ["ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE", "VOW3.DE", "BMW.DE"]
champions_us = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

def show_table(title, symbols):
    st.write(f"**{title}**")
    data_list = []
    for s in symbols:
        d = get_market_data(s)
        if d:
            data_list.append({
                "Trend": d["Trend"], "Name": d["Name"], 
                "Preis(EUR)": f"{d['Preis']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "Pos%": f"{d['RSI']}%", "ATR": d["ATR"],
                "Status": "EXTREM HOCH" if d["RSI"] > 90 else "EXTREM TIEF" if d["RSI"] < 10 else "Normal"
            })
    st.dataframe(pd.DataFrame(data_list), hide_index=True, use_container_width=True)

col_a, col_b = st.columns(2)
with col_a: show_table("Europa: Deine 7 Hidden Champions", champions_eu)
wit
