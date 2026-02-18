import os
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

def play_alarm():
    audio_html = """
        <audio autoplay style="display:none;">
            <source src="https://assets.mixkit.co" type="audio/mpeg">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh
    
st_autorefresh(interval=30000, key="datarefresh")

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
    .effektiver-wert { font-size: 11px; color: #aaaaaa; margin-top: -5px; font-weight: bold; }
    .product-label { font-size: 18px !important; font-weight: bold; color: #00ff00 !important; margin: 0; }
    .focus-header { color: #888888 !important; font-weight: bold; margin-bottom: 20px; border-bottom: 1px solid #444; padding-bottom: 5px; }
    .pos-val { color: #00ff00; }
    .neg-val { color: #ff4b4b; }
    div[data-testid="column"] { display: flex; flex-direction: column; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'triggered_breakouts' not in st.session_state:
    st.session_state.triggered_breakouts = set()

if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}

if 'history_log' not in st.session_state:
    st.session_state.history_log = []

if 'session_start' not in st.session_state:
    # Setzt Startzeit einmalig (+1h Korrektur)
    st.session_state.session_start = (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')

# Update-Zeit bei jedem Durchlauf aktualisieren (+1h Korrektur)
st.session_state.last_update = (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')

# --- 3. LOGIK ---
def get_weather_info(delta):
    if delta > 0.5: return "☀️", "SONNIG", "🟢", "BUY"
    elif delta >= 0: return "🌤️", "HEITER", "🟢", "BULL"
    elif delta > -0.5: return "☁️", "WOLKIG", "⚪", "WAIT"
    else: return "⛈️", "GEWITTER", "🔴", "SELL"

def fetch_data():
    # Liste deiner 14 ausgewählten Aktien
    symbols = {
        "AAPL": "APPLE", "MSFT": "MICROSOFT", "AMZN": "AMAZON", "NVDA": "NVIDIA", 
        "GOOGL": "ALPHABET", "META": "META", "TSLA": "TESLA",
        "ASML": "ASML", "MC.PA": "LVMH", "SAP.DE": "SAP", "NOVO-B.CO": "NOVO NORDISK", 
        "OR.PA": "L'OREAL", "ROG.SW": "ROCHE", "NESN.SW": "NESTLE"
    }
    results = {}
    aktuell = datetime.now() + timedelta(hours=1)
    current_time = aktuell.strftime('%H:%M:%S')
    st.session_state.last_update = current_time
    
    for ticker, label in symbols.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="5d") 
            if len(df) >= 2:
                curr = df['Close'].iloc[-1]
                prev_high = df['High'].iloc[-2] # Das Hoch von gestern
                is_breakout = curr > prev_high
                
                # --- ALARM AUSLÖSEN ---
                if is_breakout and label not in st.session_state.triggered_breakouts:
                    st.session_state.triggered_breakouts.add(label)
                    play_alarm()
                    st.toast(f"🚀 BREAKOUT: {label} über Vortageshoch!", icon="🔔")

                if label not in st.session_state.initial_values:
                    st.session_state.initial_values[label] = curr
                
                start = st.session_state.initial_values[label]
                delta = ((curr - start) / start) * 100 if start != 0 else 0
                w_icon, w_txt, a_icon, a_txt = get_weather_info(delta)
                
                results[label] = {
                    "price": curr, "prev_high": prev_high, "is_breakout": is_breakout,
                    "delta": delta, "w": w_icon, "wt": w_txt, "a": a_icon, "at": a_txt
                }
        except: pass
     return results

data = fetch_data()
now_display = datetime.now() - timedelta(hours=1)
datum_heute = datetime.now().strftime('%Y.%m.%d')

def render_row(label, d, f_str="{:.2f}"):
    if not d: return
    with st.container():
        cols = st.columns([0.5, 0.5, 1.5, 1.5, 1.0]) # Spalten leicht angepasst
        
        # Wetter & Signal (wie gehabt)
        with cols[0]:
            st.markdown(f"<div style='text-align:center;'><span style='font-size:20px;'>{d['w']}</span></div>", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"<div style='text-align:center;'><span style='font-size:16px;'>{d['a']}</span></div>", unsafe_allow_html=True)
            
        # Preis & Delta
        with cols[2]:
            st.metric(label="", value=f_str.format(d['price']), delta=f"{d['delta']:+.3f}%")
            
        # NEU: BREAKOUT STATUS
        with cols[3]:
            if d['is_breakout']:
                st.markdown(f"<div style='background-color:#003300; border:1px solid #00ff00; padding:5px; border-radius:5px; text-align:center;'><span style='color:#00ff00; font-size:12px; font-weight:bold;'>🚀 BREAKOUT</span><br><span style='font-size:10px;'>High: {d['prev_high']:.2f}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='padding:5px; text-align:center;'><span style='color:#444; font-size:12px;'>Under High</span><br><span style='font-size:10px; color:#666;'>{d['prev_high']:.2f}</span></div>", unsafe_allow_html=True)
        
        # Label
        with cols[4]:
            st.markdown(f"<p class='product-label' style='margin-top:12px;'>{label}</p>", unsafe_allow_html=True)

    
    # Erzeugt eine saubere Trennlinie nach jeder Reihe
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
        
# --- HEADER ---
h1, h2 = st.columns([2, 1])
with h1: st.title("📡 TERMINAL 📡")
with h2: 
   st.markdown(f"""
        <div style='text-align:right;'>
            <h2 style='margin:0; color:#e0e0e0; font-size: 28px; font-weight: bold;'>Heute: {datum_heute}</h2>
            <h2 style='margin:0; color:#00ff00; font-size: 28px; font-weight: bold;'>Update: {st.session_state.last_update}</h2>
            <hr style='margin: 10px 0 5px 0; border-color: #444;'>
            <p style='margin:0; color:#888888; font-size: 14px;'>Start: {st.session_state.session_start}</p>
        </div>
    """, unsafe_allow_html=True)
    
# --- 1. DEFAULT ANZEIGE (WÄHRUNG & INDIZES) ---
st.markdown("<p class='focus-header'>🌍 FOKUS/ GLOBAL MACRO FOCUS 🌍</p>", unsafe_allow_html=True)
render_row("EUR/USD", data.get("EUR/USD"), "{:.6f}")
render_row("S&P 500", data.get("S&P 500"), "{:.2f}")
render_row("EUROSTOXX 50", data.get("EUROSTOXX 50"), "{:.2f}")

st.markdown("<hr>", unsafe_allow_html=True)

# --- 2. EXPANDER: EUROSTOXX AKTIEN ---
with st.expander("FOKUS: € EUROPA (EUROSTOXX 50)", expanded=False):
    eu_list = ["ASML", "LVMH", "SAP", "SIEMENS", "TOTALENERGIES", "ALLIANZ", "L'OREAL"]
    for asset in eu_list:
        render_row(asset, data.get(asset))

# --- 3. EXPANDER: US TECH AKTIEN ---
with st.expander("FOKUS: 🪙 US MARKET (S&P500)", expanded=False):
    us_list = ["APPLE", "MICROSOFT", "AMAZON", "NVIDIA", "ALPHABET", "META", "TESLA"]
    for asset in us_list:
        render_row(asset, data.get(asset))

# --- 4. EXPANDER: ERKLÄRUNG & HANDLUNGSINFO ---
with st.expander("💡 MARKT-KOMPASS + HANDLUNGSINFO 💡", expanded=False):
    # Dynamische Analyse-Logik
    all_assets = list(data.values())
    if all_assets:
        sunny_count = len([a for a in all_assets if a['wt'] == "SONNIG"])
        stormy_count = len([a for a in all_assets if a['wt'] == "GEWITTER"])
        total = len(all_assets)
        
        # Volatilitäts-Check: Wie stark weichen die Werte im Schnitt ab?
        avg_delta = sum(abs(a['delta']) for a in all_assets) / total
        
        st.markdown("### 📊 AKTUELLE LAGE-ANALYSE")
        
        # 1. Stimmungs-Check
        if sunny_count > total * 0.4:
            st.success(f"🔥 **STRONG BULLISH:** {sunny_count} von {total} Werten sind im Kaufbereich. Fokus auf Long-Einstiege.")
        elif stormy_count > total * 0.4:
            st.error(f"⚠️ **BEARISH ALERT:** {stormy_count} von {total} Werten zeigen Gewitter. Absicherung hat Priorität.")
        else:
            st.info(f"⚖️ **NEUTRAL / MIXED:** Der Markt sucht eine Richtung. Abwarten empfohlen.")

        # 2. Volatilitäts-Warnung (Neu)
        if avg_delta > 1.5:
            st.warning(f"⚡ **HOHE VOLATILITÄT:** Die durchschnittliche Schwankung liegt bei {avg_delta:.2f}%. Erhöhtes Risiko für Stop-Fischer!")
        elif avg_delta < 0.2:
            st.info(f"💤 **LOW VOLA:** Markt schläft ({avg_delta:.2f}% Bewegung). Kaum Ausbruchspotenzial.")

        st.markdown("---")
    st.markdown("""
    ### 🌦️ Strategie-Legende
    *   ☀️ **SONNIG (> +0.5%):** **BUY** | Trendstärke. Gewinne laufen lassen.
    *   🌤️ **HEITER (0% bis +0.5%):** **BULL** | Stabile Lage. Rücksetzer kaufen.
    *   ☁️ **WOLKIG (0% bis -0.5%):** **WAIT** | Keine klare Richtung. Füße stillhalten.
    *   ⛈️ **GEWITTER (< -0.5%):** **SELL** | Verkaufsdruck. Short-Chancen oder Cash.
    ---
    **Hinweis:** Die Messung erfolgt gegen den Initialwert beim Start. Nutze den **Manual Refresh** für ein Reset.
    """)

# --- PROTOKOLL ---
with st.expander("📊 PROTOKOLL DER VERÄNDERUNGEN 📊"):
    if st.session_state.history_log:
        df_log = pd.DataFrame(st.session_state.history_log).iloc[::-1]
        st.dataframe(
            df_log, 
            hide_index=True, 
            use_container_width=True)

with st.sidebar:
    if st.button("🔄 MANUAL REFRESH"): st.rerun()












