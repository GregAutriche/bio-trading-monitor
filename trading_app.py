import os
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, key="datarefresh")

import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    div[data-testid="stSlider"], .stSlider { display: none !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    h1, h2, h3, p, span, label, div {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    [data-testid="stMetricValue"] { font-size: 24px !important; color: #ffffff !important; }
    [data-testid="stMetricDelta"] { font-size: 16px !important; }
    .effektiver-wert { font-size: 14px; color: #aaaaaa; margin-top: -15px; font-weight: bold; }
    .product-label { font-size: 20px !important; font-weight: bold; color: #00ff00 !important; margin-left: -20px; }
    .focus-header { color: #888888 !important; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #444; }
    
    .pos-val { color: #00ff00; font-weight: bold; }
    .neg-val { color: #ff4b4b; font-weight: bold; }
    hr { border-top: 1px solid #444; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
# Initialwerte für Assets
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}

# Historie für das Protokoll
if 'history_log' not in st.session_state:
    st.session_state.history_log = []

# Sitzungsstart (nur einmalig beim ersten Laden)
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now().strftime('%H:%M:%S')

# Letztes Update (wird bei jedem Durchlauf aktualisiert)
st.session_state.last_update = datetime.now().strftime('%H:%M:%S')

# --- 3. LOGIK ---
def get_weather_info(delta):
    if delta > 0.5: return "☀️", "SONNIG", "🟢", "BUY"
    elif delta >= 0: return "🌤️", "HEITER", "🟢", "BULL"
    elif delta > -0.5: return "☁️", "WOLKIG", "⚪", "WAIT"
    else: return "⛈️", "GEWITTER", "🔴", "SELL"

def fetch_data():
    symbols = {
        "EURUSD=X": "EUR/USD", "^GSPC": "S&P 500", "^STOXX50E": "EUROSTOXX 50",
        "AAPL": "APPLE", "MSFT": "MICROSOFT", "AMZN": "AMAZON", "NVDA": "NVIDIA", "GOOGL": "ALPHABET", "META": "META", "TSLA": "TESLA",
        "ASML": "ASML", "MC.PA": "LVMH", "SAP.DE": "SAP", "SIE.DE": "SIEMENS", "TTE.PA": "TOTALENERGIES", "ALV.DE": "ALLIANZ", "OR.PA": "L'OREAL"
    }
    results = {}
    current_time = datetime.now().strftime('%H:%M:%S')
    
    for ticker, label in symbols.items():
        try:
            t = yf.Ticker(ticker)
            # Am Wochenende (heute: 15.02.2026) liefert period="2d" die Freitagsschlusskurse
            df = t.history(period="2d") 
            if not df.empty:
                curr = df['Close'].iloc[-1]
                
                # Ersterfassung der Werte
                is_new = False
                if label not in st.session_state.initial_values:
                    st.session_state.initial_values[label] = curr
                    is_new = True # Markierung für initialen Log-Eintrag
                
                start = st.session_state.initial_values[label]
                diff = curr - start
                delta = (diff / start) * 100 if start != 0 else 0
                w_icon, w_txt, a_icon, a_txt = get_weather_info(delta)
                results[label] = {"price": curr, "delta": delta, "diff": diff, "w": w_icon, "wt": w_txt, "a": a_icon, "at": a_txt}
                
                # FIX: Logge wenn sich etwas ändert ODER wenn das Asset gerade erst geladen wurde
                if diff != 0 or is_new:
                    st.session_state.history_log.append({
                        "Zeit": current_time, "Asset": label, "Betrag": f"{curr:.4f}",
                        "Veränderung": f"{diff:+.4f}", "Anteil %": f"{delta:+.3f}%"
                    })
        except: pass
    return results

data = fetch_data()
now_display = datetime.now() - timedelta(hours=1)
datum_heute = datetime.now().strftime('%Y.%m.%d')

def render_row(label, d, f_str="{:.2f}"):
    if not d: return
    # Spaltenaufteilung: Status 1, Status 2, Werte, Label
    cols = st.columns([0.4, 0.4, 1.4, 2.0])
    
    # Farblogik
    s_color = "#00ff00" if d['delta'] > 0 else "#ff4b4b" if d['delta'] < -0.5 else "#aaaaaa"
    status_style = f"display: flex; flex-direction: column; align-items: center; line-height: 1.1; color: {s_color};"

    with cols[0]:
        st.markdown(f"<div style='{status_style}'><span style='font-size: 18px;'>{d['w']}</span><span style='font-size: 9px; font-weight: bold;'>{d['wt']}</span></div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div style='{status_style}'><span style='font-size: 14px;'>{d['a']}</span><span style='font-size: 9px; font-weight: bold;'>{d['at']}</span></div>", unsafe_allow_html=True)
    with cols[2]: 
        st.metric(label="", value=f_str.format(d['price']), delta=f"{d['delta']:+.3f}%")
        c_class = "pos-val" if d['diff'] >= 0 else "neg-val"
        d_fmt = f"{d['diff']:+.6f}" if "USD" in label or "/" in label else f"{d['diff']:+.4f}"
        st.markdown(f"<p class='effektiver-wert'>Abs: <span class='{c_class}'>{d_fmt}</span></p>", unsafe_allow_html=True)
    with cols[3]: 
        st.markdown(f"<p class='product-label'>{label}</p>", unsafe_allow_html=True)
    
# --- HEADER ---
h1, h2 = st.columns([2, 1])
with h1: st.title("☁️ TERMINAL")
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
with st.expander("📊 PROTOKOLL DER VERÄNDERUNGEN"):
    if st.session_state.history_log:
        st.table(pd.DataFrame(st.session_state.history_log).iloc[::-1].head(15))

with st.sidebar:
    if st.button("🔄 MANUAL REFRESH"): st.rerun()


















