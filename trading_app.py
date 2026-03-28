import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. DESIGN & FARBLOGIK (MIDNIGHT BLUE) ---
st.set_page_config(page_title="Trading-Terminal 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: #ffffff; } 
    div[data-testid="stTable"] { background-color: #002b55 !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #ffffff !important; background-color: #002b55 !important; }
    [data-testid="stMetric"] { background-color: #002b55; border: 1px solid #0074D9; border-radius: 10px; padding: 10px; }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    .stButton>button { background-color: #0074D9; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK: OPTIONEN ABRUFEN ---
def get_option_board(symbol):
    try:
        ticker = yf.Ticker(symbol)
        if not ticker.options:
            return None, None
        
        # Nächstes Verfallsdatum wählen
        expiry = ticker.options[0]
        opt = ticker.option_chain(expiry)
        
        # Top 5 Calls & Puts nach Open Interest
        calls = opt.calls.nlargest(5, 'openInterest')[['strike', 'lastPrice', 'openInterest']]
        puts = opt.puts.nlargest(5, 'openInterest')[['strike', 'lastPrice', 'openInterest']]
        return calls, puts
    except:
        return None, None

# --- 3. LOGIK: ANALYSE & KURSE ---
def get_analysis(ticker_dict, timeframe, is_fx=False, kontostand=25000, risiko_val=500):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if hist.empty: continue
            
            cp = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            chg_pct = ((cp / prev_close) - 1) * 100
            
            # Trend & Risiko-Berechnung
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            vol_std = hist['High'].rolling(14).std().iloc[-1]
            sl_dist = max(vol_std * 2, cp * 0.005)
            
            sl = cp - sl_dist if is_bullish else cp + sl_dist
            tp = cp + (sl_dist * 2.5) if is_bullish else cp - (sl_dist * 2.5)
            
            data_list.append({
                "Name": name, "Symbol": symbol, "Typ": "CALL" if is_bullish else "PUT",
                "Chance": f"{'75%' if is_bullish else '45%'}", "Kurs": cp, "Change": chg_pct,
                "SL": sl, "TP": tp, "CRV": round(abs(tp-cp)/abs(cp-sl), 1),
                "Hist": hist, "is_fx": is_fx
            })
        except: continue
    return data_list

# --- 4. GRAFIK-FUNKTION (OHNE MINUS-WERTE LINKS) ---
def plot_advanced_chart(item):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                        row_width=[0.2, 0.8], specs=[[{"secondary_y": True}], [{"secondary_y": False}]])
    
    # Kerzenchart (Links-Achse)
    fig.add_trace(go.Candlestick(x=item['Hist'].index, open=item['Hist']['Open'], high=item['Hist']['High'],
                    low=item['Hist']['Low'], close=item['Hist']['Close'], name="Kurs"), row=1, col=1, secondary_y=False)
    
    # Prozent-Linie (Rechts-Achse)
    pct_trace = ((item['Hist']['Close'] / item['Kurs']) - 1) * 100
    fig.add_trace(go.Scatter(x=item['Hist'].index, y=pct_trace, name="Abweichung %", 
                             line=dict(color='rgba(0, 212, 255, 0.3)'), fill='tozeroy'), row=1, col=1, secondary_y=True)
    
    # Volumen
    v_colors = ['#00ff00' if r['Open'] < r['Close'] else '#ff4b4b' for _, r in item['Hist'].iterrows()]
    fig.add_trace(go.Bar(x=item['Hist'].index, y=item['Hist']['Volume'], marker_color=v_colors, opacity=0.4), row=2, col=1)

    # Korrektur der Y-Achse (Kein Minus beim Kurs)
    fig.update_yaxes(title_text="Kurs (Absolut)", secondary_y=False, rangemode="nonnegative", row=1, col=1)
    fig.update_yaxes(title_text="Abweichung %", secondary_y=True, showgrid=False, row=1, col=1)
    
    fig.update_layout(height=500, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", 
                      xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)

# --- 5. SIDEBAR ---
st.sidebar.header("🛡️ Risikomanagement")
konto = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000)
risiko = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)

# --- 6. INDEX HEATMAP ---
st.subheader("🌍 Markt-Übersicht")
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX"}
idx_data = get_analysis(indices, "1d")
cols = st.columns(len(idx_data))
for i, item in enumerate(idx_data):
    color = "#008000" if item['Change'] >= 0 else "#800000"
    cols[i].markdown(f"<div style='background:{color};padding:10px;border-radius:5px;text-align:center;'><b>{item['Name']}</b><br>{item['Kurs']:,.2f} ({item['Change']:.2f}%)</div>", unsafe_allow_html=True)

st.divider()

# --- 7. FX & OPTION ANALYSIS ---
st.subheader("📊 Detail-Analyse & Options-Board")

# Auswahl-Logik
stocks = {
    "EURUSD=X": "💱 EUR/USD", "SAP.DE": "🇩🇪 SAP", "ADS.DE": "🇩🇪 Adidas", 
    "ALV.DE": "🇩🇪 Allianz", "DBK.DE": "🇩🇪 Deutsche Bank", "VOW3.DE": "🇩🇪 VW"
}
selected_symbol = st.selectbox("Symbol wählen", list(stocks.keys()), format_func=lambda x: stocks[x])

res_list = get_analysis({selected_symbol: stocks[selected_symbol]}, intervall, "EURUSD" in selected_symbol, konto, risiko)

if res_list:
    res = res_list[0]
    plot_advanced_chart(res)
    
    # Metriken
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Kurs", f"{res['Kurs']:.5f}" if res['is_fx'] else f"{res['Kurs']:.2f}")
    m2.metric("Trend", res['Typ'])
    m3.metric("Ziel (TP)", f"{res['TP']:.4f}")
    m4.metric("CRV", res['CRV'])

    st.divider()
    
    # OPTIONS BOARD
    st.markdown("### 🎫 Top 5 Call & Put (Open Interest)")
    calls, puts = get_option_board(selected_symbol)
    
    if calls is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h4 style='color:#00ff00;'>Calls (Bullish)</h4>", unsafe_allow_html=True)
            st.table(calls)
        with c2:
            st.markdown("<h4 style='color:#ff4b4b;'>Puts (Bearish)</h4>", unsafe_allow_html=True)
            st.table(puts)
    else:
        st.info("Für dieses Symbol (z.B. Forex) sind keine direkten Börsen-Optionsdaten via yfinance verfügbar.")

st.markdown("---")
st.caption(f"Terminal Stand: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | Daten von Yahoo Finance")
