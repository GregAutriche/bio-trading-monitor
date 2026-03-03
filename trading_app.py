import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- 1. CONFIG ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    h1, h2, h3, p, span, label, div { color: #c9d1d9 !important; font-family: 'Courier New', monospace; }
    .sig-p { color: #f85149; font-weight: bold; border: 1px solid #f85149; padding: 2px 6px; border-radius: 4px; }
    .focus-header { color: #58a6ff !important; font-weight: bold; border-bottom: 1px solid #30363d; margin: 15px 0 10px 0; }
    code { background-color: #161b22 !important; color: #f85149 !important; padding: 2px 4px; border-radius: 3px; }
    .row-wrapper { border-bottom: 1px solid #30363d; padding-bottom: 4px; margin-bottom: 4px; width: 100%; }
    .error-tag { background-color: #f85149; color: white !important; padding: 1px 4px; border-radius: 3px; font-size: 0.6rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE MIT DEEP-CLEAN ---
def analyze_ticker(ticker):
    try:
        df = yf.download(ticker, period="1mo", interval="1d", progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        is_recovered = False
        # --- DEEP CLEAN LOGIK FÜR EUR/USD ---
        if "EURUSD=X" in ticker:
            # Wir prüfen JEDEN Wert in der Historie auf Geisterwerte
            mask = (df['Close'] > 2.0) | (df['Close'] < 0.5)
            if mask.any():
                is_recovered = True
                # Ersetze alle Ausreißer durch den Median (stabilster Wert der letzten 30 Tage)
                valid_median = df.loc[~mask, 'Close'].median()
                if pd.isna(valid_median): valid_median = 1.1617
                df.loc[mask, ['Open', 'High', 'Low', 'Close']] = valid_median

        curr = float(df['Close'].iloc[-1])
        prev, prev2 = df['Close'].iloc[-2], df['Close'].iloc[-3]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        
        # ATR Berechnung auf den bereinigten Daten (verhindert Riesen-Stops)
        tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        
        signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
        # Stop-Loss ist jetzt korrekt, da ATR auf 1.16er Basis berechnet wurde
        stop = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0
        delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
        icon = "☀️" if (curr > sma20 and delta > 0.3) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.3 else "⚖️"
        
        return {"name": ticker, "price": curr, "signal": signal, "stop": stop, "delta": delta, "icon": icon, "is_recovered": is_recovered}
    except: return None

# --- 3. UI ---
def render_row(res):
    st.markdown("<div class='row-wrapper'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([1.0, 0.5, 0.3, 0.7, 0.6], gap="small")
    with c1:
        tag = "<span class='error-tag'>RECOVERED</span>" if res['is_recovered'] else ""
        st.markdown(f"**{res['name']}** {tag}<br><small>Kurs: {res['price']:.5f}</small>", unsafe_allow_html=True)
    with c2:
        col = "#3fb950" if res['delta'] >= 0 else "#f85149"
        st.markdown(f"### {res['icon']}<br><span style='font-size:0.8rem; color:{col}'>{res['delta']:+.2f}%</span>", unsafe_allow_html=True)
    with c3:
        cls = "sig-p" if res['signal'] == "P" else "sig-wait" # Vereinfacht für Beispiel
        st.markdown(f"<br><span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<small>Stop-Loss</small><br><code>{res['stop']:.5f}</code>", unsafe_allow_html=True)
    st.divider()

# APP START
st.title("📡 Strategie Check")
res = analyze_ticker("EURUSD=X")
if res: render_row(res)
