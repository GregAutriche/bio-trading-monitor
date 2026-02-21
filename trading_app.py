import os
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# --- 0. AUTO-REFRESH & ALARM-AUDIO ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=30000, key="datarefresh")

def play_alarm():
    audio_html = """
        <audio autoplay style="display:none;">
            <source src="https://assets.mixkit.co" type="audio/mpeg">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    [data-testid="stMetricValue"] { font-size: 22px !important; color: #ffffff !important; }
    [data-testid="stMetricDelta"] { font-size: 14px !important; }
    .product-label { font-size: 18px !important; font-weight: bold; color: #00ff00 !important; margin: 0; }
    .focus-header { color: #888888 !important; font-weight: bold; margin-top: 25px; border-bottom: 1px solid #444; padding-bottom: 5px; }
    .stat-box { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; margin-bottom: 15px; }
    .header-time { color: #00ff00 !important; font-size: 32px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}
if 'triggered_breakouts' not in st.session_state:
    st.session_state.triggered_breakouts = set()
if 'breakout_history' not in st.session_state:
    st.session_state.breakout_history = []
if 'session_start' not in st.session_state:
    st.session_state.session_start = (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')

# --- 3. LOGIK ---
def get_weather_info(delta):
    if delta > 0.5: return "☀️", "SONNIG", "🟢", "BUY"
    elif delta >= 0: return "🌤️", "HEITER", "🟢", "BULL"
    elif delta > -0.5: return "☁️", "WOLKIG", "⚪", "WAIT"
    else: return "⛈️", "GEWITTER", "🔴", "SELL"

def fetch_data():
    symbols = {
        "EURUSD=X": "EUR/USD", "^STOXX50E": "EUROSTOXX 50", "^IXIC": "NASDAQ",
        "^CRSLDX": "NIFTY 500 (IN)", "XU100.IS": "BIST 100 (TR)",
        "AAPL": "APPLE", "MSFT": "MICROSOFT", "AMZN": "AMAZON", "NVDA": "NVIDIA", 
        "GOOGL": "ALPHABET", "META": "META", "TSLA": "TESLA",
        "ASML": "ASML", "MC.PA": "LVMH", "SAP.DE": "SAP", "NOVO-B.CO": "NOVO NORDISK", 
        "OR.PA": "L'OREAL", "ROG.SW": "ROCHE", "NESN.SW": "NESTLE"
    }
    results = {}
    aktuell = datetime.now() + timedelta(hours=1)
    st.session_state.last_update = aktuell.strftime('%H:%M:%S')
    
    for ticker, label in symbols.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="5d") 
            if len(df) >= 2:
                curr = df['Close'].iloc[-1]
                prev_high = df['High'].iloc[-2]
                is_breakout = curr > prev_high
                
                # Alarm nur für Aktien, nicht für FX/Indizes
                if is_breakout and label not in st.session_state.triggered_breakouts and "X" not in ticker and "^" not in ticker:
                    st.session_state.triggered_breakouts.add(label)
                    st.session_state.breakout_history.append({
                        "Zeit": st.session_state.last_update, 
                        "Aktie": label, 
                        "Preis": f"{curr:.2f}"
                    })
                    play_alarm()
                    st.toast(f"🚀 BREAKOUT: {label}!", icon="🔔")

                if label not in st.session_state.initial_values:
                    st.session_state.initial_values[label] = curr
                
                delta = ((curr - st.session_state.initial_values[label]) / st.session_state.initial_values[label]) * 100
                w_icon, w_txt, a_icon, a_txt = get_weather_info(delta)
                
                results[label] = {
                    "price": curr, "prev_high": prev_high, "is_breakout": is_breakout,
                    "delta": delta, "w": w_icon, "wt": w_txt, "a": a_icon, "at": a_txt
                }
        except: pass
    return results

def render_row(label, d, f_str="{:.2f}"):
    if not d: return
    bg_color = "rgba(0, 255, 0, 0.08)" if d['is_breakout'] else "transparent"
    border_col = "#00ff00" if d['is_breakout'] else "#333"
    
    with st.container():
        st.markdown(f"<div style='background-color: {bg_color}; padding: 12px; border-radius: 10px; border: 1px solid {border_col}; border-left: 6px solid {border_col}; margin-bottom: 12px;'>", unsafe_allow_html=True)
        cols = st.columns([0.6, 0.6, 1.2, 1.4, 1.4])
        with cols[0]: st.markdown(f"<div style='text-align:center;'>{d['w']}<br><span style='font-size:9px;'>{d['wt']}</span></div>", unsafe_allow_html=True)
        with cols[1]: st.markdown(f"<div style='text-align:center;'>{d['a']}<br><span style='font-size:9px;'>{d['at']}</span></div>", unsafe_allow_html=True)
        with cols[2]: st.metric("", f_str.format(d['price']), f"{d['delta']:+.3f}%")
        with cols[3]:
            if d['is_breakout']:
                st.markdown(f"<span style='color:#00ff00; font-weight:bold;'>🚀 BREAKOUT</span><br><span style='font-size:10px;'>High: {d['prev_high']:.4f}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:#666;'>Under High</span><br><span style='font-size:10px;'>Target: {d['prev_high']:.4f}</span>", unsafe_allow_html=True)
        with cols[4]: st.markdown(f"<p class='product-label'>{label}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 4. DISPLAY ---
data = fetch_data()

# HEADER
head_cols = st.columns([2, 1])
with head_cols[0]:
    st.markdown("<h1>📡 BREAKOUT 📡</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#888; margin-top:-15px;'>Sitzungsbeginn: {st.session_state.session_start}</p>", unsafe_allow_html=True)
with head_cols[1]:
    st.markdown(f"<div style='text-align:right;'><span class='header-time'>{st.session_state.last_update}</span></div>", unsafe_allow_html=True)

# STATISTIK
if data:
    b_count = sum(1 for k, v in data.items() if v['is_breakout'] and k not in ["EUR/USD", "EUROSTOXX 50", "NASDAQ"])
    st.markdown(f"<div class='stat-box'><span style='font-size: 20px;'>Signale: <b style='color:#00ff00;'>{b_count} von 14</b> Aktien im Breakout</span></div>", unsafe_allow_html=True)

# 1. EXPANDER: HISTORIE
with st.expander("🕒 SESSION BREAKOUT LOG (HISTORIE HEUTE)", expanded=False):
    if st.session_state.breakout_history:
        st.table(pd.DataFrame(st.session_state.breakout_history[::-1]))
    else:
        st.info("Noch keine Breakouts in dieser Sitzung erfasst.")

# 2. EXPANDER: ERKLÄRUNGEN
with st.expander("ℹ️ SYMBOL-ERKLÄRUNG & HANDLUNGS-GUIDE"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Markt-Wetter:**\n- ☀️ SONNIG (>+0.5%)\n- ☁️ WOLKIG (Neutral)\n- ⛈️ GEWITTER (<-0.5%)")
    with c2:
        st.markdown("**Signale:**\n- 🚀 BREAKOUT: Über Vortages-Hoch\n- 🟢 BUY: Aktiver Trend\n- ⚪ WAIT: Unter Widerstand")

# MACO FOCUS
st.markdown("<p class='focus-header'>🌍 FOKUS/ GLOBAL MACRO 🌍</p>", unsafe_allow_html=True)
render_row("EUR/USD", data.get("EUR/USD"), "{:.6f}")
render_row("EUROSTOXX 50", data.get("EUROSTOXX 50"))
render_row("NASDAQ", data.get("NASDAQ"))
render_row("NIFTY 500 (IN)", data.get("NIFTY 500 (IN)"))
render_row("BIST ALL (TR)", data.get("BIST ALL (TR)"))

# AKTIEN SEKTIONEN
st.markdown("<p class='focus-header'>FOKUS/ 🇪🇺 EUROPA (Europa's 7)</p>", unsafe_allow_html=True)
for e in ["ASML", "LVMH", "SAP", "NOVO NORDISK", "L'OREAL", "ROCHE", "NESTLE"]:
    render_row(e, data.get(e))

st.markdown("<p class='focus-header'>FOKUS/ 🇺🇸 US TECH  (US 7)</p>", unsafe_allow_html=True)
for u in ["APPLE", "MICROSOFT", "AMAZON", "NVIDIA", "ALPHABET", "META", "TSLA"]:
    render_row(u, data.get(u))












