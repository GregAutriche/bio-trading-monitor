import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. TERMINAL LOOK (CSS) ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    [data-testid="stMetric"] {
        background-color: #0a0a0a;
        border: 1px solid #1f1f1f;
        padding: 15px;
        border-radius: 10px;
    }
    h1, h2, h3, p, span, label {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    hr { border-top: 1px solid #333; }
    /* Entfernt Standard-Abstände für kompaktere Darstellung */
    .stMarkdown div p { margin-bottom: 0px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATENFUNKTION ---
def get_live_data():
    mapping = {"EURUSD": "EURUSD=X", "STOXX": "^STOXX50E", "SP": "^GSPC"}
    results = {}
    for key, ticker in mapping.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="5d")
            if not df.empty:
                results[key] = {
                    "price": df['Close'].iloc[-1],
                    "delta": ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
                    "df": df
                }
        except: results[key] = None
    return results

data = get_live_data()
now = datetime.now()

# --- 3. HELFER-FUNKTIONEN ---
def compact_row(label, price, delta, weather_icon, weather_text, action_dot, action_text):
    # Spalten: Kursbox | Wetter | Action (eng gruppiert)
    c1, c2, c3 = st.columns([0.4, 0.4,2.5])
    with c1:
        st.metric(label, price, delta)
    with c2:
        st.markdown(f"### {weather_icon}")
        st.caption(weather_text)
    with c3:
        st.markdown(f"### {action_dot}")
        st.caption(action_text)

def stock_row(ticker, name, price, change, weather_icon, action_text, action_color):
    color_map = {"Green": "🟢", "White": "⚪", "Red": "🔴"}
    dot = color_map.get(action_color, "⚪")
    col1, col2, col3 = st.columns([2.5, 0.4, 0.4])
    with col1:
        st.markdown(f"**{ticker}** | {name} <br> `{price} ({change})`", unsafe_allow_html=True)
    with col2:
        st.markdown(f"### {weather_icon}")
    with col3:
        st.markdown(f"### {dot}")

# --- 4. HEADER (RECHTSBÜNDIGES UPDATE) ---
header_col1, header_col2 = st.columns([2, 1])
with header_col1:
    st.markdown(f"""
        <div style="text-align: right;">
            <p style="color: #888; font-size: 0.8rem;">Letztes Update:</p>
            <h3 style="margin-top: 0;">{now.strftime('%A, %H:%M')}</h3>
        </div>
        """, unsafe_allow_html=True)
with header_col2:
    st.write(f"### {now.strftime('%y%m%d')}")
    st.write(f"**LIVE TERMINAL**")


st.markdown("---")

# --- 5. SEKTIONEN ---
st.markdown("### 💱 FOKUS/ Währung")
if data["EURUSD"]:
    compact_row("EUR/USD", "☀️", "Heiter", "🟢", "Bullisch" f"{data['EURUSD']['price']:.4f}", f"{data['EURUSD']['delta']:.2f}%")

st.markdown("---")

st.markdown("### 📈 FOKUS/ Markt-Indizes")
if data["STOXX"]:
    compact_row("EURO STOXX 50", f"{data['STOXX']['price']:.2f}", f"{data['STOXX']['delta']:.2f}%", 
                "☁️", "Bewölkt", "⚪", "Wait")
st.write("")
if data["SP"]:
    compact_row("S&P INDEX", f"{data['SP']['price']:.2f}", f"{data['SP']['delta']:.2f}%", 
                "☀️", "Sonnig", "🟢", "Buy")

st.markdown("---")

st.markdown("### 📊 FOKUS/ Analyse-Grafik")
if data["SP"]:
    df_chart = data["SP"]["df"]
    fig = go.Figure(data=[go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'])])
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.markdown("### 📈 FOKUS/ Aktien")

st.subheader("/ Europa")
with st.container(border=True):
    stock_row("ASML", "ASML Holding", "942.10€", "+0.5%", "☀️", "Buy", "Green")
    st.divider()
    stock_row("SAP", "SAP SE", "178.40€", "-0.2%", "☁️", "Wait", "White")
    st.divider()
    stock_row("MC.PA", "LVMH", "845.20€", "+0.9%", "☀️", "Buy", "Green")
    st.divider()
    stock_row("SIE", "Siemens AG", "182.30€", "+0.5%", "☀️", "Buy", "Green")
    st.divider()
    stock_row("ALV", "Allianz SE", "264.10€", "+1.2%", "☀️", "Buy", "Green")
    st.divider()
    stock_row("AIR", "Airbus SE", "158.90€", "-0.2%", "☁️", "Wait", "White")
    st.divider()
    stock_row("SAN", "Sanofi", "89.40€", "+0.3%", "☁️", "Wait", "White")

st.subheader("/ USA")
with st.container(border=True):
    stock_row("NVDA", "NVIDIA Corp", "894.10$", "+3.2%", "☀️", "Buy", "Green")
    st.divider()
    stock_row("AAPL", "Apple Inc", "172.50$", "-0.7%", "🌧️", "Sell", "Red")
    st.divider()
    stock_row("MSFT", "Microsoft", "415.20$", "+0.4%", "☀️", "Buy", "Green")
    st.divider()
    stock_row("AMZN", "Amazon", "178.10$", "-0.1%", "☁️", "Wait", "White")
    st.divider()
    stock_row("META", "Meta Platforms", "485.40$", "-0.8%", "☁️", "Wait", "White")
    st.divider()
    stock_row("TSLA", "Tesla Inc", "163.20$", "-1.5%", "🌧️", "Sell", "Red")
    st.divider()
    stock_row("GOOGL", "Alphabet Inc", "148.30$", "+0.4%", "☀️", "Buy", "Green")

st.divider()
st.warning("⚠️ Risikohinweis: Algorithmisches Wetter-Modell. Keine Anlageberatung.")


