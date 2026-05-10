import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import concurrent.futures
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor", layout="wide")

# Email-Funktion
def send_alert(ticker_name, chance):
    try:
        # Zugangsdaten aus Streamlit Secrets
        conf = st.secrets["email"]
        
        msg = MIMEMultipart()
        msg['From'] = conf["sender_email"]
        msg['To'] = conf["receiver_email"]
        msg['Subject'] = f"🚀 Trading Alert: {ticker_name} ({chance}%)"
        
        body = f"Hohe Chance erkannt!\n\nAsset: {ticker_name}\nScore: {chance}%\n\nPrüfe dein Dashboard: https://streamlit.app"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(conf["smtp_server"], conf["smtp_port"])
        server.starttls()
        server.login(conf["sender_email"], conf["sender_password"])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email-Fehler: {e}")
        return False

# --- ASSETS & DATEN-LOGIK (wie zuvor) ---
ASSETS = {
    "BIO": {"BNTX": "BioNTech", "VRTX": "Vertex", "MRNA": "Moderna", "PFE": "Pfizer"},
    "TECH": {"TSLA": "Tesla", "NVDA": "Nvidia", "AAPL": "Apple"}
}
TICKER_TO_NAME = {ticker: name for region in ASSETS.values() for ticker, name in region.items()}
ALL_TICKERS = list(TICKER_TO_NAME.keys())

@st.cache_data(ttl=300)
def get_live_data(ticker):
    try:
        df = yf.download(ticker, period="60d", interval="1d", progress=False)
        if df.empty or len(df) < 20: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

def analyze_swing(ticker, df):
    cp = float(df['Close'].iloc[-1])
    prev_3d = float(df['Close'].iloc[-4])
    chg_3d = ((cp / prev_3d) - 1) * 100
    sma20 = df['Close'].rolling(20).mean().iloc[-1]
    
    # Vereinfachte Chance-Logik
    chance = 50 + (20 if cp > sma20 else -10) + (min(abs(chg_3d) * 0.5, 25))
    
    return {
        "name": TICKER_TO_NAME.get(ticker, ticker),
        "cp": cp, "chg_3d": chg_3d, "chance": round(min(chance, 99), 1),
        "df": df
    }

# --- HAUPTPROGRAMM ---
st.title("📈 Bio-Trading Monitor & Alerts")

if st.button("Marktanalyse starten & Alerts prüfen"):
    with st.spinner("Scanne Märkte..."):
        results = {}
        # Paralleles Laden
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ticker = {executor.submit(get_live_data, t): t for t in ALL_TICKERS}
            for future in concurrent.futures.as_completed(future_to_ticker):
                t = future_to_ticker[future]
                df = future.result()
                if df is not None: results[t] = analyze_swing(t, df)

        # 1. Metriken anzeigen
        cols = st.columns(len(results))
        for i, (t, res) in enumerate(results.items()):
            cols[i].metric(res['name'], f"{res['cp']:.2f}", f"{res['chg_3d']:.2f}%")

        # 2. Alert-Logik (Prüfung auf > 80% Chance)
        high_chance_found = False
        for t, res in results.items():
            if res['chance'] >= 80:
                with st.expander(f"🔔 ALERT: {res['name']} hat {res['chance']}% Score!"):
                    if st.button(f"Email-Benachrichtigung für {res['name']} senden"):
                        if send_alert(res['name'], res['chance']):
                            st.success(f"Email für {res['name']} versendet!")
                high_chance_found = True
        
        if not high_chance_found:
            st.info("Keine Assets mit einer Chance > 80% aktuell.")

        # 3. Tabelle
        df_tab = pd.DataFrame([{"Ticker": t, "Name": r["name"], "Chance %": r["chance"]} for t, r in results.items()])
        st.table(df_tab.sort_values("Chance %", ascending=False))

else:
    st.info("Klicke auf den Button oben, um die Analyse zu starten.")
