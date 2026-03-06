import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# --- 0. SETUP & AUTO-REFRESH ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60000, key="datarefresh") # 60s für große Listen empfohlen
except:
    st.warning("Bitte 'pip install streamlit-autorefresh' installieren für Auto-Update.")

# --- 1. STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-c { color: #3fb950 !important; border: 1px solid #3fb950 !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-high { color: #ffd700 !important; border: 1px solid #ffd700 !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 10px 0; }
    .indicator-label { color: #888; font-size: 0.75rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TICKER ENGINE (Dynamisch) ---
@st.cache_data(ttl=86400)
def get_all_tickers():
    # DAX 40
    try:
        dax = pd.read_html("https://en.wikipedia.org")[4]['Ticker'].tolist()
        dax = [t.replace('.', '-') + ".DE" for t in dax]
    except: dax = ["ADS.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "SAP.DE", "SIE.DE"]

    # NASDAQ 100
    try:
        nasdaq = pd.read_html("https://en.wikipedia.org")[4]['Ticker'].tolist()
    except: nasdaq = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN"]

    # EURO STOXX 50 (Auswahl der Top-Werte)
    eurostoxx = ["ASML.AS", "MC.PA", "OR.PA", "TTE.PA", "SAN.MC", "SAP.DE", "SIE.DE", "AIR.PA", "IBE.MC", "ITX.MC"]
    
    return {"DAX 🇩🇪": dax, "NASDAQ 100 🇺🇸": nasdaq, "EURO STOXX 50 🇪🇺": eurostoxx}

# --- 3. ANALYSE ENGINE (Vektorisiert) ---
def analyze_data(ticker_list):
    if not ticker_list: return []
    # Batch Download für Geschwindigkeit
    data = yf.download(ticker_list, period="1y", interval="1d", group_by='ticker', auto_adjust=True, progress=False)
    
    results = []
    for ticker in ticker_list:
        try:
            df = data[ticker].dropna()
            if len(df) < 35: continue
            
            # Indikatoren
            close = df['Close']
            sma20 = close.rolling(20).mean()
            
            # RSI
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # ATR für Stop-Loss
            high_low = df['High'] - df['Low']
            atr = high_low.rolling(14).mean()
            
            # ADX (vereinfacht für Performance)
            adx = (abs(high_low.diff()) / high_low).rolling(14).mean() * 100

            # Aktuelle Werte
            curr, prev, prev2 = close.iloc[-1], close.iloc[-2], close.iloc[-3]
            curr_sma = sma20.iloc[-1]
            curr_rsi = rsi.iloc[-1]
            curr_adx = adx.iloc[-1]
            
            # Signal Logik
            signal = "Wait"
            if curr > prev > prev2 and curr > curr_sma: signal = "C"
            elif curr < prev < prev2 and curr < curr_sma: signal = "P"
            
            # Wahrscheinlichkeit (Backtest 30 Tage)
            hits, total = 0, 0
            for i in range(-35, -5):
                c, p, p2 = close.iloc[i], close.iloc[i-1], close.iloc[i-2]
                s = sma20.iloc[i]
                sig = "C" if (c > p > p2 and c > s) else "P" if (c < p < p2 and c < s) else None
                if sig == signal and signal != "Wait":
                    total += 1
                    future_price = close.iloc[i+3]
                    if (signal == "C" and future_price > c) or (signal == "P" and future_price < c):
                        hits += 1
            prob = (hits / total * 100) if total > 0 else 50.0

            # Result zusammenbauen
            stop = curr - (atr.iloc[-1] * 1.5) if signal == "C" else curr + (atr.iloc[-1] * 1.5)
            delta_pct = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100

            results.append({
                "ticker": ticker, "price": curr, "delta": delta_pct, "signal": signal,
                "prob": prob, "rsi": curr_rsi, "adx": curr_adx, "stop": stop
            })
        except: continue
    return results

# --- 4. UI RENDERER ---
def render_dashboard(results):
    if not results:
        st.write("Keine Daten verfügbar.")
        return

    # Sortierung nach Wahrscheinlichkeit
    results = sorted(results, key=lambda x: x['prob'], reverse=True)

    for res in results:
        with st.container():
            c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1.5])
            with c1:
                st.markdown(f"**{res['ticker']}**")
                rsi_col = "#ff4b4b" if res['rsi'] > 70 else "#3fb950" if res['rsi'] < 30 else "#888"
                st.markdown(f"<span class='indicator-label'>RSI: <b style='color:{rsi_col}'>{res['rsi']:.1f}</b> | ADX: {res['adx']:.1f}</span>", unsafe_allow_html=True)
            
            with c2:
                color = "#3fb950" if res['delta'] > 0 else "#007bff"
                st.markdown(f"<span style='color:{color}'>{res['price']:.2f}</span><br><small>{res['delta']:+.2f}%</small>", unsafe_allow_html=True)
            
            with c3:
                if res['signal'] != "Wait":
                    cls = "sig-box-high" if res['prob'] >= 60 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
                    st.markdown(f"<span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
                else: st.markdown("---")

            with c4:
                if res['signal'] != "Wait":
                    p_color = "#ffd700" if res['prob'] >= 60 else "#888"
                    st.markdown(f"<small>Prob:</small> <b style='color:{p_color}'>{res['prob']:.1f}%</b><br><small>SL:</small> <b>{res['stop']:.2f}</b>", unsafe_allow_html=True)
            
            st.markdown("<div class='row-container'></div>", unsafe_allow_html=True)

# --- 5. MAIN ---
st.markdown("<h2 style='text-align:center;'>📡 Dr. Gregor Bauer Strategie Pro 2026</h2>", unsafe_allow_html=True)
st.write(f"Zentraler Scan-Zeitpunkt: {datetime.now().strftime('%H:%M:%S')} (Interval: 60s)")

with st.expander("ℹ️ Strategie-Leitfaden"):
    st.markdown("""
    - **C (Call):** Kurs über SMA20 + 3 Tage steigend.
    - **P (Put):** Kurs unter SMA20 + 3 Tage fallend.
    - **Gold-Signal:** Trefferquote > 60% im Backtest.
    - **RSI-Warnung:** Grün (<30) = Überverkauft, Rot (>70) = Überkauft.
    """)

ticker_groups = get_all_tickers()
tabs = st.tabs(list(ticker_groups.keys()))

for i, (name, tickers) in enumerate(ticker_groups.items()):
    with tabs[i]:
        with st.spinner(f"Scanne {len(tickers)} Werte von {name}..."):
            data_results = analyze_data(tickers)
            render_dashboard(data_results)

