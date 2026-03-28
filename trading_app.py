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
    .stButton>button { background-color: #0074D9; color: white; font-weight: bold; width: 100%; border: none; height: 3em; border-radius: 5px; }
    /* Slider Styling */
    .stSelectSlider { padding-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK: ANALYSE-FUNKTION ---
def get_analysis_data(symbol, timeframe="1h"):
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="60d", interval=timeframe)
        if hist.empty: return None
        return hist
    except: return None

# --- 3. GRAFIK-FUNKTION (DUAL AXIS & VOLUMEN) ---
def plot_advanced_chart(hist, title, current_price):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                        row_width=[0.2, 0.8], specs=[[{"secondary_y": True}], [{"secondary_y": False}]])
    
    # Candlesticks (Links-Achse)
    fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'],
                    low=hist['Low'], close=hist['Close'], name="Kurs"), row=1, col=1, secondary_y=False)
    
    # Abweichung % (Rechts-Achse)
    pct_trace = ((hist['Close'] / current_price) - 1) * 100
    fig.add_trace(go.Scatter(x=hist.index, y=pct_trace, name="Abweichung %", 
                             line=dict(color='#00d4ff', width=1.5)), row=1, col=1, secondary_y=True)
    
    # Volumen (Unten)
    v_colors = ['#00ff00' if r['Open'] < r['Close'] else '#ff4b4b' for _, r in hist.iterrows()]
    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=v_colors, opacity=0.5, name="Volumen"), row=2, col=1)

    # Achsen-Konfiguration (Kein Minus beim Preis)
    fig.update_yaxes(title_text="Kurs", secondary_y=False, rangemode="nonnegative", row=1, col=1)
    fig.update_yaxes(title_text="Abweichung %", secondary_y=True, showgrid=False, row=1, col=1)
    
    fig.update_layout(height=600, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", 
                      xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=40,b=0), title=f"Fokus-Analyse: {title}")
    st.plotly_chart(fig, use_container_width=True)

# --- 4. SIDEBAR ---
st.sidebar.header("⚙️ Terminal-Setup")
intervall = st.sidebar.selectbox("Zeitintervall für Charts", ["1h", "1d", "15m", "5m"], index=0)
st.sidebar.divider()
st.sidebar.info("Der Scanner analysiert das Netto-Sentiment (Open Interest) der wichtigsten US-Tech-Werte.")

# --- 5. INDEX-HEATMAP ---
st.subheader("🌍 Markt-Übersicht (Live Indizes)")
idx_map = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "EURUSD=X": "EUR/USD", "^STOXX50E": "EURO STOXX"}
cols = st.columns(len(idx_map))
for i, (sym, name) in enumerate(idx_map.items()):
    try:
        t = yf.Ticker(sym)
        cp = t.fast_info['last_price']
        chg = ((cp / t.fast_info['previous_close']) - 1) * 100
        bg = "#008000" if chg >= 0 else "#800000"
        cols[i].markdown(f"<div style='background:{bg};padding:10px;border-radius:8px;text-align:center;'><b>{name}</b><br>{chg:.2f}%</div>", unsafe_allow_html=True)
    except: continue

st.divider()

# --- 6. TOP SENTIMENT SCANNER ---
st.subheader("📊 Top 5 Markt-Sentiment Scanner")

if st.button("🚀 Markt nach Netto-Chance scannen"):
    scan_list = {"TSLA": "Tesla", "NVDA": "Nvidia", "AAPL": "Apple", "MSFT": "Microsoft", "AMZN": "Amazon", "META": "Meta", "AMD": "AMD"}
    all_stats = []
    
    with st.spinner('Analysiere Options-Volumen...'):
        for sym, name in scan_list.items():
            try:
                t = yf.Ticker(sym)
                if t.options:
                    opt = t.option_chain(t.options[0]) # Nächstes Verfallsdatum
                    c_oi = opt.calls['openInterest'].sum()
                    p_oi = opt.puts['openInterest'].sum()
                    total = c_oi + p_oi
                    
                    if c_oi > p_oi:
                        sentiment, chance, val = "BULLISH", (c_oi / total) * 100, c_oi
                    else:
                        sentiment, chance, val = "BEARISH", (p_oi / total) * 100, p_oi

                    all_stats.append({
                        "Aktie": name, "Symbol": sym, "Chance": chance, 
                        "Sentiment": sentiment, "Volumen (OI)": val
                    })
            except: continue

    if all_stats:
        df = pd.DataFrame(all_stats).sort_values(by='Chance', ascending=False)
        st.session_state['results'] = df # Speichern für den Slider
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🟢 Top Bullish (Überwiegend Calls)")
            bulls = df[df['Sentiment'] == "BULLISH"].head(5)
            st.dataframe(bulls[['Aktie', 'Chance', 'Volumen (OI)']].style.format({"Chance": "{:.1f}%", "Volumen (OI)": "{:,.0f}"}), hide_index=True, use_container_width=True)
        with c2:
            st.markdown("#### 🔴 Top Bearish (Überwiegend Puts)")
            bears = df[df['Sentiment'] == "BEARISH"].head(5)
            st.dataframe(bears[['Aktie', 'Chance', 'Volumen (OI)']].style.format({"Chance": "{:.1f}%", "Volumen (OI)": "{:,.0f}"}), hide_index=True, use_container_width=True)

# --- 7. DER DYNAMISCHE GRAFIK-SLIDER ---
if 'results' in st.session_state:
    st.divider()
    st.subheader("🔍 Detail-Fokus: Chart & Volumen")
    
    results = st.session_state['results']
    # Liste für den Slider erstellen (Name + Chance)
    slider_options = [f"{row['Aktie']} ({row['Chance']:.1f}%)" for _, row in results.iterrows()]
    
    # Der Slider zur Auswahl der Aktie
    selected_choice = st.select_slider(
        "Wähle eine Aktie aus dem Scan aus, um die detaillierte Grafik mit Volumen anzuzeigen:",
        options=slider_options
    )
    
    # Symbol aus der Auswahl extrahieren
    sel_name = selected_choice.split(" (")[0]
    sel_row = results[results['Aktie'] == sel_name].iloc[0]
    sel_sym = sel_row['Symbol']
    
    # Chart-Daten laden & anzeigen
    hist_data = get_analysis_data(sel_sym, intervall)
    if hist_data is not None:
        plot_advanced_chart(hist_data, sel_name, hist_data['Close'].iloc[-1])
    else:
        st.error("Fehler beim Laden der Chart-Daten.")

st.markdown("---")
st.caption(f"Terminal Stand: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | Modus: Interaktiver Sentiment-Fokus")
