import os
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 0. FEHLERBEHEBUNG: AUTOMATISCHE INSTALLATION ---
try:
    import lxml
except ImportError:
    os.system('pip install lxml')

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

# 45 Sekunden Refresh
st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Dr. Bauer Strategie-Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .ticker-name { color: #00ff00; font-size: 18px; font-weight: bold; margin-bottom: 0px; }
    .open-price { color: #888888; font-size: 12px; margin-top: -5px; }
    .method-box { background-color: #111; padding: 15px; border-radius: 5px; border-left: 3px solid #00ff00; font-size: 14px; line-height: 1.6; }
    .weather-icon { font-size: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK FUNKTIONEN ---
@st.cache_data(ttl=3600)
def get_index_tickers():
    try:
        # Lädt DAX und NASDAQ 100 via Wikipedia
        dax = pd.read_html("https://en.wikipedia.org")[4]['Ticker'].tolist()
        dax = [f"{t}.DE" for t in dax]
        ndx = pd.read_html("https://en.wikipedia.org", attrs={'id': "constituents"})[0]['Ticker'].tolist()
        return {"DAX": dax, "NASDAQ 100": ndx}
    except Exception as e:
        return {"ERROR": [f"Fehler: {e}"]}

def analyze_bauer(df):
    if len(df) < 20: return None
    curr = df['Close'].iloc[-1]
    open_t = df['Open'].iloc[-1]
    prev_high = df['High'].iloc[-2]
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    delta = ((curr - open_t) / open_t) * 100
    
    # Candlestick-Stärke (Schluss im oberen Drittel)
    upper_wick = df['High'].iloc[-1] - max(curr, open_t)
    is_strong = upper_wick < (abs(curr - open_t) * 0.35)
    
    # Wetter & Stop (1.5x ATR)
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    icon = "☀️" if (curr > sma20 and delta > 0.5) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.5 else "☁️"
    
    return {
        "price": curr, "open": open_t, "delta": delta, "icon": icon,
        "signal": (curr > prev_high) and is_strong and (curr > sma20),
        "stop": curr - (atr * 1.5)
    }

# --- 3. UI RENDERING ---
st.title("📡 Dr. Bauer Strategie-Screener")
st.write(f"Refreshed: {datetime.now().strftime('%H:%M:%S')} | Intervall: 45s")

# DIE VERLORENE BESCHREIBUNG (METHODIK-EXPANDER)
with st.expander("📖 AUSFÜHRLICHE BESCHREIBUNG DER STRATEGIE-LOGIK"):
    st.markdown("""
    <div class='method-box'>
    <b>1. Börsen-Wetter (Trend-Indikator):</b><br>
    Das Wetter basiert auf der Lage zum <b>SMA 20</b>. Ein sonniges Icon (☀️) erscheint nur im bestätigten Aufwärtstrend (Kurs > SMA 20) bei gleichzeitiger Tagesdynamik.<br><br>
    
    <b>2. Candlestick-Stärke (Bauer-Filter):</b><br>
    Ein Signal wird nur generiert, wenn die aktuelle Tageskerze "Überzeugung" zeigt. Das Script prüft, ob der Kurs im <b>oberen Drittel</b> der Tagesspanne schließt. Lange Dochte oben (Erschöpfung) führen zur Entwertung des Signals.<br><br>
    
    <b>3. Breakout-Logik:</b><br>
    Ein 🚀 Signal erfordert das gleichzeitige Zusammentreffen von:<br>
    - Kurs über gestrigem Tageshoch (Breakout).<br>
    - Kurs über dem gleitenden Durchschnitt (SMA 20).<br>
    - Positive Candlestick-Stärke.<br><br>
    
    <b>4. Vola-Stop-Management:</b><br>
    Der Stop-Loss wird dynamisch mittels der <b>ATR (Average True Range)</b> berechnet. Der Puffer von 1.5 * ATR schützt vor zufälligem Marktrauschen.
    </div>
    """, unsafe_allow_html=True)

# SCREENING START
index_data = get_sp500_tickers()
selected_index = st.radio("Wähle Index zum Scannen:", list(index_data.keys()), horizontal=True)

if st.button(f"Scan {selected_index} jetzt starten"):
    with st.spinner(f"Analysiere {len(index_data[selected_index])} Werte nach Dr. Bauer..."):
        results = []
        for ticker in index_data[selected_index]:
            try:
                data = yf.Ticker(ticker).history(period="1mo")
                analysis = analyze_bauer(data)
                if analysis:
                    results.append({"Ticker": ticker, **analysis})
            except: continue
        
        # Sortierung: Signale zuerst, dann nach Performance
        df_res = pd.DataFrame(results).sort_values(by=["signal", "delta"], ascending=False)
        
        # Display
        for _, row in df_res.iterrows():
            c = st.columns([1, 1, 1, 1, 1])
            c[0].markdown(f"**{row['Ticker']}**<br><small>Start: {row['open']:.2f}</small>", unsafe_allow_html=True)
            c[1].markdown(f"## {row['icon']}")
            c[2].metric("Kurs", f"{row['price']:.2f}", f"{row['delta']:+.2f}%")
            c[3].markdown(f"## {'🚀' if row['signal'] else 'Wait'}")
            c[4].warning(f"Stop: {row['stop']:.2f}")
            st.divider()
