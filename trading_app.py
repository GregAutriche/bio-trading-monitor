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
    .stTable td, .stTable th { color: #ffffff !important; background-color: #002b55 !important; border-bottom: 1px solid #0074D9 !important; }
    [data-testid="stMetric"] { background-color: #002b55; border: 1px solid #0074D9; border-radius: 10px; }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; font-size: 0.9rem !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    .stButton>button { background-color: #0074D9; color: white; font-weight: bold; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: #00d4ff; font-size: 0.8rem;'>Update: {last_update}</p>", unsafe_allow_html=True)

# --- 2. ANALYSE-LOGIK (3-10 TAGE & KAPITAL-SICHERUNG) ---
def get_analysis(ticker_dict, timeframe, is_fx=False, kontostand=25000, risiko=500):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if hist.empty or len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            chg_pct = ((cp / prev_close) - 1) * 100
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            vol = hist['High'].rolling(14).std().iloc[-1]
            sl_dist_raw = vol * 2 if vol > 0 else cp * 0.005
            
            # 100% Kapital-Sicherung: SL weiten, falls Einsatz zu hoch
            min_sl_dist = (risiko * cp) / kontostand if not is_fx else (risiko * cp) / (kontostand / 100)
            final_dist = max(sl_dist_raw, min_sl_dist)
            
            sl = cp - final_dist if is_bullish else cp + final_dist
            tp = cp + (final_dist * 2.5) if is_bullish else cp - (final_dist * 2.5)
            
            chance_val = 75 if is_bullish else 45
            risk_unit = abs(cp - sl)
            lots = round(risiko / (risk_unit * 10000), 4) if is_fx else int(risiko / risk_unit)
            kap_pct = ((lots * 100000 * cp if is_fx else lots * cp) / kontostand) * 100

            data_list.append({
                "Name": name, "Symbol": symbol, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Chance": f"{chance_val}%", "Chance_Val": chance_val, "Kurs": cp, "Change": chg_pct,
                "Kapitaleinsatz": f"{min(kap_pct, 100.0):.2f}%", "SL": sl, "TP": tp, "Hist": hist
            })
        except: continue
    return data_list

# --- 3. SIDEBAR ---
st.sidebar.header("🛡️ Risikomanagement")
konto = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000)
risiko = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)

# --- 4. INDEX-HEATMAP (OBEN) ---
st.subheader("🌍 Index-Heatmap (24h Change & Wert)")
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX", "^NSEI": "NIFTY", "XU100.IS": "BIST 100"}
idx_data = get_analysis(indices, "1d", False, konto, risiko)

if idx_data:
    cols = st.columns(len(idx_data))
    for i, item in enumerate(idx_data):
        bg_color = "#008000" if item['Change'] >= 0 else "#800000"
        with cols[i]:
            st.markdown(f"""
                <div style="background-color: {bg_color}; border: 1px solid #0074D9; border-radius: 10px; padding: 12px; text-align: center;">
                    <span style="color: #b0c4de; font-size: 0.8rem; display: block; margin-bottom: 2px;">{item['Name']}</span>
                    <span style="color: #ffffff; font-size: 1.1rem; font-weight: bold; display: block;">{item['Kurs']:,.0f}</span>
                    <span style="color: #ffffff; font-size: 0.9rem; opacity: 0.9;">{item['Change']:.2f}%</span>
                </div>
            """, unsafe_allow_html=True)

st.divider()

# --- 5. EUR/USD ANALYSE MIT GRAFIK ---
st.subheader("💱 EUR/USD Live-Analyse")
fx_res = get_analysis({"EURUSD=X": "EUR/USD"}, intervall, True, konto, risiko)
if fx_res:
    res = fx_res[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Kurs", f"{res['Kurs']:.5f}")
    c2.metric("Chance", res['Chance'])
    c3.metric("Kapitaleinsatz", res['Kapitaleinsatz'])

    fig_fx = make_subplots(specs=[[{"secondary_y": True}]])
    fig_fx.add_trace(go.Candlestick(x=res['Hist'].index, open=res['Hist']['Open'], high=res['Hist']['High'], low=res['Hist']['Low'], close=res['Hist']['Close'], name="Kurs"), secondary_y=False)
    fig_fx.add_hline(y=res['TP'], line_dash="dash", line_color="#00ff00", annotation_text="Ziel (TP)")
    fig_fx.add_hline(y=res['SL'], line_dash="dash", line_color="#ff4b4b", annotation_text="Stopp (SL)")
    fig_fx.update_layout(height=350, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig_fx, use_container_width=True)

st.divider()

# --- 6. TOP 5 AKTIEN CHANCEN ---
st.subheader("🔥 Top 5 Aktien-Chancen")
stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall", "TSLA": "Tesla", "AAPL": "Apple", "MSFT": "Microsoft"}
all_stock_results = get_analysis(stocks, intervall, False, konto, risiko)

if all_stock_results:
    df = pd.DataFrame(all_stock_results)
    col_l, col_r = st.columns(2)
    with col_l:
        st.success("Top 5 CALL (Long)")
        calls = df[df['Typ'] == "CALL 🟢"].sort_values("Chance_Val", ascending=False).head(5)
        st.table(calls[["Name", "Chance", "Kapitaleinsatz", "Kurs"]])
    with col_r:
        st.error("Top 5 PUT (Short)")
        puts = df[df['Typ'] == "PUT 🔴"].sort_values("Chance_Val", ascending=False).head(5)
        st.table(puts[["Name", "Chance", "Kapitaleinsatz", "Kurs"]])

    st.divider()

    # --- 7. AKTIEN DETAIL-ANALYSE MIT GRAFIK ---
    st.subheader("🔍 Aktien Detail-Ansicht")
    selection = st.selectbox("Aktie wählen:", df['Name'].tolist())
    if selection:
        item = next(x for x in all_stock_results if x['Name'] == selection)
        c1, c2, c3 = st.columns(3)
        c1.metric("Kurs", f"{item['Kurs']:.2f}")
        c2.metric("Ziel (TP)", f"{item['TP']:.2f}")
        c3.metric("Stopp (SL)", f"{item['SL']:.2f}")

        fig_stock = make_subplots(specs=[[{"secondary_y": True}]])
        fig_stock.add_trace(go.Candlestick(x=item['Hist'].index, open=item['Hist']['Open'], high=item['Hist']['High'], low=item['Hist']['Low'], close=item['Hist']['Close'], name="Kurs"), secondary_y=False)
        fig_stock.add_hline(y=item['TP'], line_dash="dash", line_color="#00ff00", annotation_text="TP")
        fig_stock.add_hline(y=item['SL'], line_dash="dash", line_color="#ff4b4b", annotation_text="SL")
        fig_stock.update_layout(height=400, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_stock, use_container_width=True)
