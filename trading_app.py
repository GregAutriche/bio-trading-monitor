import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from collections import OrderedDict

# --- 0. CONFIG & NAVY DESIGN ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

st.markdown("""
    <style>
    .stApp { background-color: #0a192f; }
    h1, h2, h3, p, span, label, div { color: #e6f1ff !important; font-family: 'Segoe UI', sans-serif; }
    .header-text { font-size: 26px; font-weight: bold; color: #64ffda !important; border-bottom: 2px solid #64ffda; padding-bottom: 5px; margin-bottom: 15px; }
    
    /* Signal Design */
    .sig-box-c { color: #00ff41 !important; border: 1px solid #00ff41; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(0, 255, 65, 0.1); }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(0, 123, 255, 0.1); }
    
    /* Sparkline Fix: Entfernt Achsen, Hintergrund und Labels */
    [data-testid="stVegaLiteChart"] { background-color: transparent !important; margin-top: -30px !important; }
    .row-container { border-bottom: 1px solid #172a45; padding: 8px 0; margin: 0; }
    .metric-label { color: #8892b0; font-size: 0.75rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. SIDEBAR ---
st.sidebar.header("🛡️ Risiko-Parameter")
capital = st.sidebar.number_input("Gesamtkapital (€)", value=10000)
risk_pct = st.sidebar.slider("Risiko (%)", 0.1, 5.0, 1.0)
risk_amount = capital * (risk_pct / 100)

# --- 2. MARKT-DATEN ---
@st.cache_data(ttl=3600)
def get_market_maps():
    maps = {}
    try:
        df_dax = pd.read_html("https://en.wikipedia.org")[4]
        maps["DAX 40 🇩🇪"] = dict(zip([t.replace('.', '-') + ".DE" for t in df_dax['Ticker-Symbol']], df_dax['Unternehmen']))
        df_ndx = pd.read_html("https://en.wikipedia.org")[4]
        maps["NASDAQ 100 🇺🇸"] = dict(zip(df_ndx['Ticker'], df_ndx['Company']))
        df_es50 = pd.read_html("https://en.wikipedia.org")[3]
        maps["EURO STOXX 50 🇪🇺"] = dict(zip(df_es50['Ticker'], df_es50['Name']))
    except: pass

    maps["INDICES & FOREX 🌍"] = OrderedDict([
        ("EURUSD=X", "EUR/USD"), ("^STOXX50E", "EUROSTOXX"), ("^GDAXI", "DAX"),
        ("^IXIC", "NASDAQ"), ("EURRUB=X", "EUR/RUB"), ("^NSEI", "NIFTY"), ("XU100.IS", "BIST")
    ])
    return maps

# --- 3. ENGINE ---
def analyze(ticker_map, filter_active=True):
    tickers = list(ticker_map.keys())
    data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', auto_adjust=True, progress=False)
    results = []
    for ticker, name in ticker_map.items():
        try:
            df = data[ticker].dropna() if len(tickers) > 1 else data.dropna()
            close = df['Close']
            sma20 = close.rolling(20).mean()
            curr, p1, p2 = close.iloc[-1], close.iloc[-2], close.iloc[-3]
            signal = "C" if (curr > p1 > p2 and curr > sma20.iloc[-1]) else "P" if (curr < p1 < p2 and curr < sma20.iloc[-1]) else "Wait"
            
            if filter_active and signal == "Wait": continue
            
            atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
            sl = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5)
            stk = int(risk_amount / abs(curr - sl)) if abs(curr - sl) > 0 else 0
            
            results.append({
                "name": name, "ticker": ticker, "price": curr, "signal": signal, "stop": sl, "stk": stk,
                "rsi": 100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean()))).iloc[-1],
                "delta": ((curr/df['Open'].iloc[-1])-1)*100, "spark": close.tail(15)
            })
        except: continue
    return results

# --- 4. UI ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie Pro 2026</div>", unsafe_allow_html=True)

with st.expander("ℹ️ VOLLSTÄNDIGER STRATEGIE-LEITFADEN & REGELWERK ℹ️", expanded=True):
    st.markdown("""
    ### 1. Marktzustand & Trend-Indikator
    Die Marktverfassung wird primär über den gleitenden Durchschnitt (SMA 20) bestimmt:
    - **Bullish:** Kurs liegt stabil über dem SMA 20. Fokus auf Call-Signale.
    - **Bearish:** Kurs liegt unter dem SMA 20. Fokus auf Put-Signale.
    
    ### 2. Signal-Trigger (3-Tage-Regel)
    Ein valides Signal benötigt eine Bestätigung des Momentums:
    - **C (Call):** Kurs über SMA 20 UND steigende Tendenz an drei aufeinanderfolgenden Tagen.
    - **P (Put):** Kurs unter SMA 20 UND fallende Tendenz an drei aufeinanderfolgenden Tagen.
    
    ### 3. Risikomanagement (Stop-Loss & Stk.)
    - **Stop-Loss (SL):** Automatische Berechnung bei 1,5x ATR (Volatilität), um Marktrauschen zu ignorieren.
    - **Stk. (Stückzahl):** Der Rechner ermittelt basierend auf dem Abstand zum SL und deinem eingestellten Risiko die exakte Anzahl der zu handelnden Einheiten.
    
    ### 4. RSI-Warnung
    Der RSI (14) dient als Filter:
    - Werte **> 70** (Rot): Markt ist überhitzt, Korrekturgefahr bei Call-Signalen.
    - Werte **< 30** (Grün): Markt ist überverkauft, Erholungschance bei Put-Signalen.
    """)

m_maps = get_market_maps()
tabs = st.tabs(list(m_maps.keys()))

for i, (tab_name, t_map) in enumerate(m_maps.items()):
    with tabs[i]:
        is_fixed = ("FOREX" in tab_name)
        data_res = analyze(t_map, filter_active=not is_fixed)
        for res in data_res:
            st.markdown("<div class='row-container'>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([2, 1, 0.5, 1.5])
            with c1:
                st.markdown(f"**{res['name']}**")
                # Sparkline-Fix: area_chart ohne Achsenbeschriftung
                st.area_chart(res['spark'], height=45, use_container_width=True)
            with c2:
                fmt = "{:.5f}" if "=" in res['ticker'] else "{:.2f}"
                st.markdown(f"**{fmt.format(res['price'])}**")
                st.markdown(f"<span class='metric-label'>RSI: {res['rsi']:.1f}</span>", unsafe_allow_html=True)
            with c3:
                if res['signal'] != "Wait":
                    cls = "sig-box-c" if res['signal'] == "C" else "sig-box-p"
                    st.markdown(f"<span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
                else: st.markdown("<span style='color:#333;'>WAIT</span>")
            with c4:
                if res['signal'] != "Wait":
                    st.markdown(f"**{res['stk']} Stk.**")
                    st.markdown(f"<span class='metric-label'>SL: {fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
