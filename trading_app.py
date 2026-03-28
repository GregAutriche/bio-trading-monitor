import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DESIGN & STYLE ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: #ffffff; } 
    [data-testid="stMetric"] { background-color: #002b55; padding: 15px; border-radius: 10px; border: 1px solid #0074D9; }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    .stTable { background-color: #002b55; color: white; }
    .stButton>button { background-color: #0074D9; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: #00d4ff;'>Update: {last_update}</p>", unsafe_allow_html=True)
st.title("🚀 Trading-Monitor: 100% Kapital-Sicherung")

# --- 2. SIDEBAR ---
st.sidebar.header("🛡️ Risikomanagement")
kontostand = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000, step=1000)
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)
top_n = st.sidebar.slider("Top-Signale", 1, 10, 5)

# --- 3. ANALYSE-LOGIK MIT 100% SPERRE ---
def get_analysis(ticker_dict, timeframe, is_fx=False):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            # SL-Berechnung (Volatilität)
            vol = hist['High'].rolling(10).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.02
            
            # --- SICHERHEITS-LOGIK: 100% KAPITAL-LIMIT ---
            # Max. Positionsgröße = Kontostand
            # Risiko pro Einheit darf nicht so klein sein, dass Pos > Kontostand
            min_sl_dist = (risiko_eur * cp) / kontostand if not is_fx else (risiko_eur * cp) / (kontostand / 100) # Vereinfacht für FX
            
            # Wenn technischer SL zu eng ist (Kapital > 100%), SL weiten
            final_sl_dist = max(sl_dist, min_sl_dist)
            sl = cp - final_sl_dist if is_bullish else cp + final_sl_dist
            tp = cp + (final_sl_dist * 2.5) if is_bullish else cp - (final_sl_dist * 2.5)

            # Positions-Kalkulation
            risk_per_unit = abs(cp - sl)
            if is_fx:
                lots = round(risiko_eur / (risk_per_unit * 10000), 4)
                pos_wert = lots * 100000 * cp
            else:
                stueck = int(risiko_eur / risk_per_unit)
                pos_wert = stueck * cp
            
            kapital_pct = (pos_wert / kontostand) * 100
            
            # Wahrscheinlichkeit
            prob = 60 + (15 if is_bullish else 0)
            status = "🔥 TOP" if prob >= 75 else "✅ OK"

            data_list.append({
                "Name": name, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{prob}%", "Prob_Val": prob,
                "Kurs": round(cp, 5 if is_fx else 2),
                "Kapitaleinsatz": f"{min(kapital_pct, 100.0):.2f}%",
                "SL": round(sl, 5 if is_fx else 2), "TP": round(tp, 5 if is_fx else 2),
                "Status": status, "Hist": hist
            })
        except: continue
    return data_list

# --- 4. EUR/USD ANZEIGE ---
st.subheader("💱 EUR/USD Live (Max. 100% Kapital)")
fx_res = get_analysis({"EURUSD=X": "EUR/USD"}, intervall, is_fx=True)

if fx_res:
    res = fx_res[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kurs", f"{res['Kurs']:.5f}")
    c2.metric("Wahrscheinlichkeit", res['Wahrscheinlichkeit'])
    c3.metric("Kapitaleinsatz", res['Kapitaleinsatz'])
    c4.info(f"**SL:** {res['SL']:.5f} | **TP:** {res['TP']:.5f}")

    fig = go.Figure(data=[go.Candlestick(x=res['Hist'].index, open=res['Hist']['Open'], 
                    high=res['Hist']['High'], low=res['Hist']['Low'], close=res['Hist']['Close'], name="EUR/USD")])
    fig.add_hline(y=res['TP'], line_dash="dash", line_color="#00ff00", annotation_text="Ziel")
    fig.add_hline(y=res['SL'], line_dash="dash", line_color="#ff4b4b", annotation_text="Stopp (angepasst)")
    fig.update_layout(height=350, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=10,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 5. AKTIEN SCAN ---
if st.button("🚀 Großen Markt-Scan starten"):
    stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall", "TSLA": "Tesla"}
    all_stocks = get_analysis(stocks, intervall)
    if all_stocks:
        df = pd.DataFrame(all_stocks)
        l, r = st.columns(2)
        with l:
            st.success(f"Top {top_n} CALLS")
            st.table(df[df['Typ'] == "CALL 🟢"].head(top_n)[["Name", "Wahrscheinlichkeit", "Kapitaleinsatz", "Kurs"]])
        with r:
            st.error(f"Top {top_n} PUTS")
            st.table(df[df['Typ'] == "PUT 🔴"].head(top_n)[["Name", "Wahrscheinlichkeit", "Kapitaleinsatz", "Kurs"]])

st.caption("ℹ️ Das Programm weitet den Stop-Loss automatisch aus, falls der Kapitaleinsatz 100% übersteigen würde.")
