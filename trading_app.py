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
    div[data-testid="stTable"], div[data-testid="stDataFrame"] { 
        background-color: #002b55 !important; 
        border-radius: 10px; 
    }
    [data-testid="stMetric"] { 
        background-color: #002b55; 
        border: 1px solid #0074D9; 
        border-radius: 10px; 
        padding: 10px; 
    }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; font-size: 0.9rem !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: bold; }
    .stButton>button { background-color: #0074D9; color: white; font-weight: bold; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK: OPTIONEN ABRUFEN (KORRIGIERT) ---
def get_option_board(symbol):
    try:
        t = yf.Ticker(symbol)
        if not t.options:
            return None, None
        
        # Nächstes Verfallsdatum wählen
        expiry = t.options[0]
        opt = t.option_chain(expiry)
        
        # Top 5 Calls & Puts nach Open Interest (OI) extrahieren
        calls = opt.calls.nlargest(5, 'openInterest')[['strike', 'lastPrice', 'openInterest']]
        puts = opt.puts.nlargest(5, 'openInterest')[['strike', 'lastPrice', 'openInterest']]
        
        # Sortieren nach Strike (für die "Leiter"-Optik) & Index bereinigen
        calls = calls.sort_values(by='strike').reset_index(drop=True)
        puts = puts.sort_values(by='strike').reset_index(drop=True)
        
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
            if hist.empty or len(hist) < 5: continue
            
            cp = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            chg_pct = ((cp / prev_close) - 1) * 100
            
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

# --- 4. GRAFIK-FUNKTION (KORRIGIERTE ACHSEN) ---
def plot_advanced_chart(item):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                        row_width=[0.2, 0.8], specs=[[{"secondary_y": True}], [{"secondary_y": False}]])
    
    # Kerzen (Links-Achse)
    fig.add_trace(go.Candlestick(x=item['Hist'].index, open=item['Hist']['Open'], high=item['Hist']['High'],
                    low=item['Hist']['Low'], close=item['Hist']['Close'], name="Kurs"), row=1, col=1, secondary_y=False)
    
    # Abweichung (Rechts-Achse)
    pct_trace = ((item['Hist']['Close'] / item['Kurs']) - 1) * 100
    fig.add_trace(go.Scatter(x=item['Hist'].index, y=pct_trace, name="Abweichung %", 
                             line=dict(color='#00d4ff', width=1)), row=1, col=1, secondary_y=True)
    
    # Volumen
    v_colors = ['#00ff00' if r['Open'] < r['Close'] else '#ff4b4b' for _, r in item['Hist'].iterrows()]
    fig.add_trace(go.Bar(x=item['Hist'].index, y=item['Hist']['Volume'], marker_color=v_colors, opacity=0.4, name="Volumen"), row=2, col=1)

    # Korrektur: Kein Minus links & saubere Beschriftung
    fig.update_yaxes(title_text="Kurs (Absolut)", secondary_y=False, rangemode="nonnegative", row=1, col=1)
    fig.update_yaxes(title_text="Abweichung %", secondary_y=True, showgrid=False, row=1, col=1)
    fig.update_layout(height=500, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", 
                      xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- 5. SIDEBAR & HEATMAP ---
st.sidebar.header("🛡️ Risikomanagement")
konto = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000)
risiko = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall wählen", ["1d", "1h", "15m", "5m"], index=0)

st.subheader("🌍 Index-Heatmap")
idx_map = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX", "^NSEI": "NIFTY", "XU100.IS": "BIST 100"}
idx_res = get_analysis(idx_map, "1d")
if idx_res:
    cols = st.columns(len(idx_res))
    for i, it in enumerate(idx_res):
        bg = "#008000" if it['Change'] >= 0 else "#800000"
        cols[i].markdown(f"<div style='background:{bg};padding:10px;border-radius:8px;text-align:center;'><b>{it['Name']}</b><br>{it['Change']:.2f}%</div>", unsafe_allow_html=True)

st.divider()

# --- 6. EUR/USD & AKTIEN DETAIL ---
st.subheader("📊 Detail-Analyse & Options-Board")

# Auswahl: Währungen + DAX/US Aktien für Options-Tests
assets = {
    "EURUSD=X": "💱 EUR/USD", 
    "TSLA": "🇺🇸 Tesla (Top Options-Daten)",
    "SAP.DE": "🇩🇪 SAP",
    "ADS.DE": "🇩🇪 Adidas",
    "DBK.DE": "🇩🇪 Deutsche Bank"
}
sel_asset = st.selectbox("Symbol wählen", list(assets.keys()), format_func=lambda x: assets[x])

res_list = get_analysis({sel_asset: assets[sel_asset]}, intervall, "EURUSD" in sel_asset, konto, risiko)

if res_list:
    item = res_list[0]
    plot_advanced_chart(item)
    
    # Metriken
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Kurs", f"{item['Kurs']:.5f}" if item['is_fx'] else f"{item['Kurs']:.2f}")
    m2.metric("Chance", item['Chance'])
    m3.metric("Richtung", item['Typ'])
    m4.metric("CRV", f"{item['CRV']}")

    st.divider()
    
    # --- OPTIONS BOARD (BEREINIGT) ---
    st.markdown("### 🎫 Top 5 Call & Put (Open Interest)")
    calls, puts = get_option_board(sel_asset)
    
    if calls is not None:
        c_col, p_col = st.columns(2)
        # Formatierung: 2 Nachkommastellen für Preise, keine Index-Spalte
        with c_col:
            st.markdown("<h4 style='color:#00ff00;'>🟢 Calls (Bullish)</h4>", unsafe_allow_html=True)
            st.dataframe(calls.style.format({"strike": "{:.2f}", "lastPrice": "{:.2f}", "openInterest": "{:,.0f}"}), 
                         hide_index=True, use_container_width=True)
        with p_col:
            st.markdown("<h4 style='color:#ff4b4b;'>🔴 Puts (Bearish)</h4>", unsafe_allow_html=True)
            st.dataframe(puts.style.format({"strike": "{:.2f}", "lastPrice": "{:.2f}", "openInterest": "{:,.0f}"}), 
                         hide_index=True, use_container_width=True)
    else:
        st.info("Keine Optionsdaten für dieses Symbol (z.B. Forex oder DAX via Yahoo) verfügbar. Teste 'Tesla' für Live-Daten.")

st.caption(f"Terminal Stand: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | 2026 Pro Trader")
