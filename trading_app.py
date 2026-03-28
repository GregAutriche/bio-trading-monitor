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
    div[data-testid="stDataFrame"] { background-color: #002b55 !important; border-radius: 10px; }
    [data-testid="stMetric"] { background-color: #002b55; border: 1px solid #0074D9; border-radius: 10px; padding: 10px; }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; font-size: 0.9rem !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: bold; }
    .stButton>button { background-color: #0074D9; color: white; font-weight: bold; width: 100%; border: none; height: 3em; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK: ANALYSE-FUNKTION ---
def get_analysis(ticker_dict, timeframe, is_fx=False):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if hist.empty: continue
            
            cp = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            chg_pct = ((cp / prev_close) - 1) * 100
            
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            data_list.append({
                "Name": name, "Symbol": symbol, "Typ": "CALL" if is_bullish else "PUT",
                "Chance": "75%" if is_bullish else "45%", "Kurs": cp, "Change": chg_pct,
                "Hist": hist, "is_fx": is_fx
            })
        except: continue
    return data_list

# --- 3. GRAFIK-FUNKTION (SAUBERE ACHSEN) ---
def plot_advanced_chart(item):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                        row_width=[0.2, 0.8], specs=[[{"secondary_y": True}], [{"secondary_y": False}]])
    
    # Kurs (Links)
    fig.add_trace(go.Candlestick(x=item['Hist'].index, open=item['Hist']['Open'], high=item['Hist']['High'],
                    low=item['Hist']['Low'], close=item['Hist'].Close, name="Kurs"), row=1, col=1, secondary_y=False)
    
    # Abweichung (Rechts)
    pct_trace = ((item['Hist']['Close'] / item['Kurs']) - 1) * 100
    fig.add_trace(go.Scatter(x=item['Hist'].index, y=pct_trace, name="Abweichung %", line=dict(color='#00d4ff', width=1)), row=1, col=1, secondary_y=True)
    
    # Volumen
    v_colors = ['#00ff00' if r['Open'] < r['Close'] else '#ff4b4b' for _, r in item['Hist'].iterrows()]
    fig.add_trace(go.Bar(x=item['Hist'].index, y=item['Hist']['Volume'], marker_color=v_colors, opacity=0.4), row=2, col=1)

    fig.update_yaxes(title_text="Kurs (Absolut)", secondary_y=False, rangemode="nonnegative", row=1, col=1)
    fig.update_yaxes(title_text="Abweichung %", secondary_y=True, showgrid=False, row=1, col=1)
    fig.update_layout(height=450, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- 4. SIDEBAR ---
st.sidebar.header("⚙️ Einstellungen")
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)

# --- 5. INDEX-HEATMAP ---
st.subheader("🌍 Markt-Heatmap")
idx_map = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "EURUSD=X": "EUR/USD", "^STOXX50E": "EURO STOXX"}
idx_res = get_analysis(idx_map, "1d")
if idx_res:
    cols = st.columns(len(idx_res))
    for i, it in enumerate(idx_res):
        bg = "#008000" if it['Change'] >= 0 else "#800000"
        cols[i].markdown(f"<div style='background:{bg};padding:10px;border-radius:8px;text-align:center;'><b>{it['Name']}</b><br>{it['Change']:.2f}%</div>", unsafe_allow_html=True)

st.divider()

# --- 6. EUR/USD LIVE ---
st.subheader("💱 EUR/USD Fokus")
fx_data = get_analysis({"EURUSD=X": "EUR/USD"}, intervall, True)
if fx_data:
    res_fx = fx_data[0]
    plot_advanced_chart(res_fx)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Kurs", f"{res_fx['Kurs']:.5f}")
    m2.metric("Trend", res_fx['Typ'])
    m3.metric("Chance", res_fx['Chance'])
    m4.metric("Change", f"{res_fx['Change']:.2f}%")

st.divider()

# --- 7. TOP 5 CALL & PUT SCANNER (MARKT-ÜBERSICHT) ---
st.subheader("📊 Top 5 Markt-Sentiment (Open Interest)")
st.markdown("Welche Aktien haben aktuell das höchste Options-Volumen?")

if st.button("🚀 Markt nach Top-Optionen scannen"):
    with st.spinner('Scanne liquide Märkte...'):
        # Liste von US-Tech Werten (liefern verlässliche Optionsdaten via Yahoo)
        scan_list = {
            "TSLA": "Tesla", "NVDA": "Nvidia", "AAPL": "Apple", 
            "MSFT": "Microsoft", "AMZN": "Amazon", "META": "Meta", "AMD": "AMD"
        }
        
        market_stats = []
        for sym, name in scan_list.items():
            try:
                t = yf.Ticker(sym)
                if t.options:
                    opt = t.option_chain(t.options[0]) # Nächstes Verfallsdatum
                    market_stats.append({
                        "Aktie": name,
                        "Calls_OI": opt.calls['openInterest'].sum(),
                        "Puts_OI": opt.puts['openInterest'].sum()
                    })
            except: continue

        if market_stats:
            df_m = pd.DataFrame(market_stats)
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("#### 🟢 Top 5 Calls (Bullish)")
                top_c = df_m.nlargest(5, 'Calls_OI')[['Aktie', 'Calls_OI']]
                st.dataframe(top_c.style.format({"Calls_OI": "{:,.0f}"}), hide_index=True, use_container_width=True)
                
            with c2:
                st.markdown("#### 🔴 Top 5 Puts (Bearish)")
                top_p = df_m.nlargest(5, 'Puts_OI')[['Aktie', 'Puts_OI']]
                st.dataframe(top_p.style.format({"Puts_OI": "{:,.0f}"}), hide_index=True, use_container_width=True)
        else:
            st.warning("Keine Optionsdaten gefunden.")

st.markdown("---")
st.caption(f"Terminal Stand: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | 2026 Pro Trader")
