import os
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# --- 0. AUTO-REFRESH & ALARM ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=30000, key="datarefresh")

def play_alarm():
    audio_html = """<audio autoplay style="display:none;"><source src="https://assets.mixkit.co" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    [data-testid="stMetricValue"] { font-size: 22px !important; color: #ffffff !important; }
    .stat-box { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; margin-bottom: 15px; }
    .header-time { color: #00ff00 !important; font-size: 32px !important; font-weight: bold; }
    .focus-header { color: #888888 !important; font-weight: bold; margin-top: 25px; border-bottom: 1px solid #444; padding-bottom: 5px; }
    .streamlit-expanderHeader { background-color: #111111 !important; color: #00ff00 !important; border-radius: 5px; font-weight: bold; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'initial_values' not in st.session_state: st.session_state.initial_values = {}
if 'triggered_s' not in st.session_state: st.session_state.triggered_s = set()
if 'breakout_history' not in st.session_state: st.session_state.breakout_history = []
if 'session_start' not in st.session_state:
    st.session_state.session_start = (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')

# --- 3. LOGIK ---
def get_weather_info(delta):
    if delta > 0.5: return "☀️", "SONNIG", "🟢", "BUY"
    elif delta >= 0: return "🌤️", "HEITER", "🟢", "BULL"
    elif delta > -0.5: return "⚪", "WOLKIG", "⚪", "WAIT"
    else: return "⛈️", "GEWITTER", "🔴", "SELL"

def fetch_data():
    symbols = {
        "EURUSD=X": "EUR/USD", "^STOXX50E": "EUROSTOXX 50", "^IXIC": "NASDAQ",
        "^CRSLDX": "NIFTY 500 (IN)", "XU100.IS": "BIST 100 (TR)", "XUTUM.IS": "BIST ALL (TR)",
        "RTSI.ME": "RTS INDEX (RU/USD)", "IMOEX.ME": "MOEX RUSSIA (RU)", "RUB=X": "USD/RUB (Währung)",
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
            df = t.history(period="7d")
            if len(df) >= 2:
                curr = df['Close'].iloc[-1]
                prev_high = df['High'].iloc[-2]
                
                d_low, d_high = df['Low'].iloc[-1], df['High'].iloc[-1]
                w_low, w_high = df['Low'].tail(5).min(), df['High'].tail(5).max()
                
                is_breakout = curr > prev_high
                
                if is_breakout and label not in st.session_state.triggered_s and "X" not in ticker and "^" not in ticker:
                    st.session_state.triggered_s.add(label)
                    st.session_state.breakout_history.append({"Zeit": st.session_state.last_update, "Aktie": label, "Preis": f"{curr:.2f}"})
                    play_alarm()
                    st.toast(f"🚀 BREAKOUT: {label}!", icon="🔔")

                if label not in st.session_state.initial_values:
                    st.session_state.initial_values[label] = curr
                
                delta = ((curr - st.session_state.initial_values[label]) / st.session_state.initial_values[label]) * 100
                w_icon, w_txt, a_icon, a_txt = get_weather_info(delta)
                
                results[label] = {
                    "price": curr, "prev_high": prev_high, "is_breakout": is_breakout,
                    "delta": delta, "w": w_icon, "wt": w_txt, "a": a_icon, "at": a_txt,
                    "d_range": (d_low, d_high), "w_range": (w_low, w_high)
                }
        except: pass
    return results

def draw_range_bar(current, low, high, title):
    total = high - low
    pos = ((current - low) / total * 100) if total != 0 else 50
    pos = max(0, min(100, pos))
    color = "#00ff00" if pos > 80 else "#ff4b4b" if pos < 20 else "#555555"
    st.markdown(f"""
        <div style="margin-bottom:8px;">
            <div style="font-size:9px; color:#888; margin-bottom:2px;">{title}</div>
            <div style="width:100%; background:#222; height:4px; border-radius:2px;">
                <div style="width:{pos}%; background:{color}; height:4px; border-radius:2px;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:8px; color:#444; margin-top:2px;">
                <span>{low:.2f}</span><span>{high:.2f}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_row(label, d, f_str="{:.2f}"):
    if not d: return
    bg_color = "rgba(0, 255, 0, 0.04)" if d['is_breakout'] else "transparent"
    border_col = "#00ff00" if d['is_breakout'] else "#222222"
    status_color = "#00ff00" if d['is_breakout'] else "#555555"
    
    with st.container():
        st.markdown(f"<div style='background-color: {bg_color}; padding: 8px 12px; border-radius: 8px; border: 1px solid {border_col}; margin-bottom: 2px;'><div style='color: #00ff00; font-size: 14px; font-weight: bold;'>{label}</div></div>", unsafe_allow_html=True)
        cols = st.columns([0.4, 0.4, 1.2, 0.8, 0.8, 0.6]) 
        
        with cols[0]: st.markdown(f"<div style='text-align:center;'><span style='font-size:28px;'>{d['w']}</span><br><span style='font-size:9px; color:#888;'>{d['wt']}</span></div>", unsafe_allow_html=True)
        with cols[1]: st.markdown(f"<div style='text-align:center;'><span style='font-size:28px;'>{d['a']}</span><br><span style='font-size:9px; color:#888;'>{d['at']}</span></div>", unsafe_allow_html=True)
        with cols[2]: st.metric("", f_str.format(d['price']), f"{d['delta']:+.3f}%")
        with cols[3]: draw_range_bar(d['price'], d['d_range'][0], d['d_range'][1], "TAGES-SPANNE")
        with cols[4]: draw_range_bar(d['price'], d['w_range'][0], d['w_range'][1], "WOCHEN-SPANNE")
        with cols[5]:
            st.markdown(f"<div style='text-align: right; line-height: 1.1;'><span style='color:{status_color}; font-size:18px; font-weight:bold;'>{'🚀' if d['is_breakout'] else 'Wait'}</span><br><span style='font-size:12px; color:#888;'>Ziel: {d['prev_high']:.2f}</span></div>", unsafe_allow_html=True)

# --- 4. DISPLAY ---
data = fetch_data()

# HEADER
h_col1, h_col2 = st.columns([2,1])
with h_col1:
    st.markdown("<h1>📡 BREAKOUT 📡</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#888; margin-top:-15px;'>Sitzung: {st.session_state.session_start}</p>", unsafe_allow_html=True)
with h_col2:
    st.markdown(f"<div style='text-align:right;'><span class='header-time'>{st.session_state.last_update}</span></div>", unsafe_allow_html=True)

# STATS
if data:
    b_count = sum(1 for k, v in data.items() if v['is_breakout'] and k not in ["EUR/USD", "EUROSTOXX 50", "NASDAQ"])
    st.markdown(f"<div class='stat-box'><span style='font-size: 18px;'>Signale: <b style='color:#00ff00;'>{b_count} Aktive Breakouts</b></span></div>", unsafe_allow_html=True)

# GUIDE EXPANDER
with st.expander("ℹ️ SYMBOL-ERKLÄRUNG & HANDLUNGS-GUIDE ℹ️"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Markt-Wetter:**\n- ☀️ SONNIG (>+0.5%)\n- ☁️ WOLKIG (Neutral)\n- ⛈️ GEWITTER (<-0.5%)")
    with c2:
        st.markdown("**Signale:**\n- 🚀 BREAKOUT: Über Vortages-Hoch\n- 🟢 BUY: Aktiver Trend\n- ⚪ WAIT: Unter Widerstand")

# 4. LOGS
with st.expander("🕒 SESSION LOG (HISTORY) 🕒", expanded=False):
    if st.session_state.breakout_history:
        # 1. Erstelle DataFrame
        df = pd.DataFrame(st.session_state.breakout_history)

    if 'Preis' in df.columns:
            df['Preis'] = pd.to_numeric(df['Preis'])
            df['Differenz zu letztem Tageshoch'] = df['Preis'] - TAGESHOCH_GESTERN
        
        # 2. Entferne Duplikate (behalte nur das erste Vorkommen der Aktie)
        # 3. Sortiere neu (Neueste Zeit nach oben) mit [::-1]
        df_unique = df.drop_duplicates(subset=['Aktie'], keep='first')[::-1]
        
        # Anzeige
        st.table(df_unique)
    else:
        st.info("Noch keine Breakouts in dieser Sitzung erfasst.")

# 1. MACRO (Immer sichtbar)
st.markdown("<p class='focus-header'>🌍 FOKUS/ MACRO 🌍</p>", unsafe_allow_html=True)
render_row("EUR/USD", data.get("EUR/USD"), "{:.5f}")
render_row("EUROSTOXX 50", data.get("EUROSTOXX 50"))
render_row("NASDAQ", data.get("NASDAQ"))
render_row("NIFTY 500 (IN)", data.get("NIFTY 500 (IN)"))
render_row("BIST 100 (TR)", data.get("BIST 100 (TR)"))
if data.get("RTS INDEX (RU/USD)"):
    render_row("RTS INDEX (RU/USD)", data.get("RTS INDEX (RU/USD)"))
elif data.get("MOEX RUSSIA (RU)"):
    render_row("MOEX RUSSIA (RU)", data.get("MOEX RUSSIA (RU)"))
else:
    # Zeigt die Währung an, falls keine Index-Daten kommen
    render_row("USD/RUB (Währung)", data.get("USD/RUB (Währung)"), "{:.4f}")

# 2. USA TECH (Expander)
with st.expander(" 🍕 FOKUS/ 🇺🇸 US TECH 🍕", expanded=False):
    for ticker in ["APPLE", "MICROSOFT", "AMAZON", "NVIDIA", "ALPHABET", "META", "TESLA"]:
        render_row(ticker, data.get(ticker))

# 3. EUROPE GROWTH (Expander)
with st.expander("🍔🏈 FOKUS/ 🇪🇺 EUROPEAN 🏈🍔", expanded=False):
    for ticker in ["ASML", "LVMH", "SAP", "NOVO NORDISK"]:
        render_row(ticker, data.get(ticker))






