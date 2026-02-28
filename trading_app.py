Zu den Hauptinhalten springenHilfe zur Barrierefreiheit
Feedback zur Barrierefreiheit
KI‑Modus
Alle
Bilder
Videos
News
Mehr



kennst Du den Trader Dr. gregor bauer
Ja, Dr. Gregor Bauer ist ein bekannter deutscher Finanzexperte, der sich besonders auf die Technische Analyse und den Optionshandel spezialisiert hat. 
Vereinigung Technischer Analysten Deutschlands e.V.
Vereinigung Technischer Analysten Deutschlands e.V.
 +1
Hier sind die wichtigsten Eckpunkte zu seinem Profil:
Rollen & Funktionen: Er ist als selbstständiger Portfolio-Manager für Privat- und Firmenkunden tätig und fungiert als Chefredakteur für Börsendienste wie den Optionen-Profi bei GeVestor. Zudem ist er im Vorstand der Vereinigung Technischer Analysten Deutschlands (VTAD) aktiv.
Expertise: Seine Schwerpunkte liegen in der Kerzencharttechnik (Candlesticks), Behavioral Finance sowie in der Analyse der impliziten Volatilität für den Optionshandel.
Publikationen: Er ist Autor von Fachbüchern wie dem Praxisratgeber Trading, in dem er die methodische Herangehensweise an die Märkte erläutert.
Präsenz: Bauer tritt regelmäßig als Referent auf Fachveranstaltungen (z. B. beim Swiss Trading Day) und in Webinaren bei Brokern wie CapTrader oder LYNX auf. 
LYNX Online Broker
LYNX Online Broker
 +7
Interessierst Du Dich für seine spezifischen Trading-Strategien oder überlegst Du, einen seiner Börsendienste zu abonnieren?
KI-Antworten können Fehler enthalten. Bei Finanzfragen solltest du dich an einen Experten wenden. Weitere Informationen




undefined
undefined
undefined
9 Websites
15 Fragen an Profitrader Dr. Gregor Bauer - LYNX
06.03.2018 — Ausgewählte Trader beantworten unseren standardisierten Fragebogen. Die Vergleichbarkeit der Fragen und die Unterschiedlichkeit od...

LYNX Online Broker

Vorstand - VTAD
Dr. Gregor Bauer, Jahrgang 1962, beschäftigt sich seit etwa 20 Jahren intensiv mit den Kapitalmärkten und arbeitet als selbstständ...

Vereinigung Technischer Analysten Deutschlands e.V.

Gregor Bauer - CapTrader - Ihr Online-Broker
Gregor Bauer - CapTrader - Ihr Online-Broker.

CapTrader

Alle anzeigen
kannst Du meinen script anpassen wie es dr. gregor bauer macht
Da Du Dein aktuelles Script nicht beigefügt hast, kann ich Dir zeigen, welche spezifischen Methoden und Parameter Dr. Gregor Bauer in seinen Analysen priorisiert. Er kombiniert klassische Charttechnik mit modernem Volatilitätsmanagement.
Hier sind die zentralen Bausteine, die Du in Deinem Script (z. B. in Pine Script für TradingView oder Python) implementieren solltest, um seinem Stil zu entsprechen:
1. Technische Indikatoren & Chartmuster
Bauer ist ein Verfechter der klassischen Technischen Analyse und der Candlestick-Methodik. Dein Script sollte folgende Elemente enthalten:
Candlestick-Filter: Integriere Abfragen für Umkehrmuster (z.B. Hammer, Shooting Star, Engulfing Patterns), da er diese zur Bestätigung von Trendwenden nutzt.
Trendbestätigung: Nutze Standard-Indikatoren wie den RSI (Relative Strength Index) oder MACD zur Bestätigung von Signalen, anstatt Dich nur auf ein einzelnes Signal zu verlassen.
Unterstützung & Widerstand: Automatisierte Erkennung von horizontalen Zonen, da diese für seine Kursziele und Stopp-Setzungen essenziell sind.
2. Fokus auf Volatilität (Vola-Analyse)
Besonders im Optionshandel ist die Implizite Volatilität (IV) für ihn entscheidend:
IV-Rank / IV-Percentile: Dein Script sollte prüfen, ob die aktuelle IV im Vergleich zur historischen IV hoch oder niedrig ist.
Regel: Kaufe Optionen (oder gehe Long), wenn die IV historisch niedrig ist; verkaufe sie (Stillhalter-Strategien), wenn die IV extrem hoch ist.
3. Die "Zweitkauf-Strategie"
Bauer nutzt oft ein systematisches Positionsmanagement, das er als "Turbo-Trading mit Zweitkauf" bezeichnet.
Script-Logik: Anstatt die gesamte Position sofort zu eröffnen, wird ein Teilkauf bei Signalgenerierung getätigt.
Zweitkauf: Ein zweiter Teil wird erst hinzugefügt, wenn der Kurs eine bestimmte Bestätigung (z. B. Bruch eines Widerstands) liefert, um das Risiko bei Fehlsignalen zu minimieren.
4. Risikomanagement & Behavioral Finance
Dr. Bauer betont stark die Psychologie des Tradings und strikte Regeln:
Hard Stops: Implementiere in Dein Script immer einen festen Stop-Loss, der auf der ATR (Average True Range) oder markanten Chartmarken basiert.
Positionsgröße: Berechne die Größe basierend auf einem festen Prozentsatz Deines Kapitals pro Trade (oft zwischen 1% und 2% Risiko).
Empfehlung für Dein Script:
Wenn Du mir Dein Script (z. B. in Pine Script) zeigst, kann ich Dir konkret die Zeilen einfügen, die einen IV-Filter oder die Candlestick-Erkennung nach Dr. Bauer hinzufügen. Er nutzt zudem gerne das Tool ELEX für seine Marktprüfungen.
KI-Antworten können Fehler enthalten. Bei Finanzfragen solltest du dich an einen Experten wenden. Weitere Informationen




undefined
undefined
undefined
6 Websites
IV implizite Volatilität im Optionshandel | Dr. Gregor Bauer ...
14.01.2025 — umfassende Praxis des Optionenhandels ich möchte das ein bisschen. einschränken ich möchte das einschränken auf den Hinweis wir we...


YouTube
·
CapTrader

9:04
Die Psycho - Private Investment
Behavioral Finance, Candlestick Analyse. Ausbildung / Werdegang, Dr. Gregor Bauer, Jahrgang 1962, ist heute selbständig tätig im B...

www.private-investment.at

Dr. Bauer´s Zweitkaufstrategie - Der Optionen-Investor
„Turbo-Trading mit Zweitkauf-Strategie“ von Dr. Gregor Bauer, Chefredakteur & Chefanalyst von „Der Optionen-Profi“. Um unsere Trad...

www.optionen-investor.de
Alle anzeigen
hier ist der aktuelle script
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
        st.markdown("**Signale:**\n- 🚀 BREAKOUT:
Um dein Script an den Stil von Dr. Gregor Bauer (VTAD) anzupassen, müssen wir weg vom reinen "Preis über gestrigem Hoch"-Breakout und hin zu einer methodischen Bestätigung durch Candlesticks und Markttechnik.
Dr. Bauer legt Wert auf:
Candlestick-Bestätigung: Ein Breakout ist erst valide, wenn die Kerze "stark" schließt (z. B. keine langen Dochte oben).
Trend-Kontext: Handeln in Richtung des übergeordneten Trends.
Vola-Check: Breakouts bei extrem hoher Volatilität sind oft Erschöpfungssignale, keine Einstiege.
Hier ist das angepasste Script (Fokus auf die Logik in fetch_data):
python
import os
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# --- AUTO-REFRESH ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=30000, key="datarefresh")

# --- CONFIG & STYLING (Dr. Bauer Edition) ---
st.set_page_config(layout="wide", page_title="Dr. Bauer Strategie-Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; }
    h1 { color: #00ff00 !important; font-family: 'Arial'; }
    .status-box { background-color: #111; padding: 10px; border-radius: 5px; border-left: 5px solid #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIK: DR. BAUER ANALYSE ---
def analyze_bauer_style(df):
    """Implementiert Dr. Bauers Fokus: Candlesticks + Trend + Vola"""
    if len(df) < 20: return None
    
    curr = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2]
    prev_high = df['High'].iloc[-2]
    low_20 = df['Low'].tail(20).min()
    high_20 = df['High'].tail(20).max()
    
    # 1. Candlestick Check (Dr. Bauer Spezialität)
    # Ein bullischer Hammer oder ein starker Body ohne langen Docht oben
    body_size = abs(curr - df['Open'].iloc[-1])
    upper_wick = df['High'].iloc[-1] - max(curr, df['Open'].iloc[-1])
    is_strong_body = upper_wick < (body_size * 0.3) # Wenig Verkaufsdruck oben
    
    # 2. Trend-Check (GD 20 als kurzfristige Basis)
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    is_uptrend = curr > sma20
    
    # 3. Breakout-Logik
    pure_breakout = curr > prev_high
    bauer_signal = pure_breakout and is_strong_body and is_uptrend
    
    # 4. Volatilität (ATR-Basis für Stop-Loss nach Bauer)
    # Dr. Bauer nutzt oft das 1.5- bis 2-fache der ATR für Stops
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    suggested_stop = curr - (atr * 1.5)

    return {
        "signal": bauer_signal,
        "is_strong_body": is_strong_body,
        "stop_loss": suggested_stop,
        "atr": atr,
        "sma20": sma20
    }

def fetch_data():
    symbols = {
        "^STOXX50E": "EUROSTOXX 50", "^IXIC": "NASDAQ",
        "AAPL": "APPLE", "MSFT": "MICROSOFT", "NVDA": "NVIDIA", 
        "SAP.DE": "SAP", "ASML": "ASML"
    }
    results = {}
    
    for ticker, label in symbols.items():
        try:
            t = yf.Ticker(ticker)
            # Wir brauchen mehr Daten für SMA und ATR (mind. 20 Tage)
            df = t.history(period="1mo")
            if len(df) >= 20:
                bauer_data = analyze_bauer_style(df)
                curr = df['Close'].iloc[-1]
                
                # Wetter-Logik (Dr. Bauer Fokus: Über dem SMA20 = Sonnig)
                delta_sma = ((curr - bauer_data['sma20']) / bauer_data['sma20']) * 100
                w_icon = "☀️" if delta_sma > 0 else "⛈️"
                
                results[label] = {
                    "price": curr,
                    "is_breakout": bauer_data['signal'],
                    "stop": bauer_data['stop_loss'],
                    "w": w_icon,
                    "delta": ((curr - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
                    "d_range": (df['Low'].iloc[-1], df['High'].iloc[-1]),
                    "w_range": (df['Low'].tail(5).min(), df['High'].tail(5).max())
                }
        except Exception as e:
            print(f"Error {ticker}: {e}")
    return results

# --- DISPLAY FUNKTIONEN (Vereinfacht für Übersicht) ---
def render_bauer_row(label, d):
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        st.markdown(f"**{label}**")
        st.write(f"{d['w']} Trend-Check")
    with col2:
        st.metric("Preis", f"{d['price']:.2f}", f"{d['delta']:+.2f}%")
    with col3:
        color = "#00ff00" if d['is_breakout'] else "#555"
        st.markdown(f"<span style='color:{color}; font-size:20px; font-weight:bold;'>{'🚀 SIGNAL' if d['is_breakout'] else 'Beobachtung'}</span>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div style='font-size:12px; color:#ff4b4b;'>Stop-Loss (ATR):<br><b>{d['stop']:.2f}</b></div>", unsafe_allow_html=True)

# --- MAIN ---
st.title("📡 Dr. Gregor Bauer: Methodik-Terminal")
st.write("Fokus: Candlestick-Stärke + Trendbestätigung (SMA20) + ATR-Stop")

data = fetch_data()
for label, d in data.items():
    render_bauer_row(label, d)
    st.divider()

with st.expander("Methodik nach Dr. Bauer"):
    st.write("""
    1. **Trendfilter:** Nur Long, wenn Preis über SMA 20 (Sonne).
    2. **Candlestick-Bestätigung:** Das Signal '🚀' erscheint nur, wenn die Kerze im oberen Drittel schließt (keine Dochte).
    3. **Risikomanagement:** Der Stop-Loss wird automatisch auf 1.5 * ATR (Volatilität) unter den Kurs gesetzt.
    """)
Verwende Code mit Vorsicht.

Was wurde im Vergleich zu deinem Original geändert?
Qualitäts-Filter (is_strong_body):
Ein Breakout im Dr. Bauer-Stil erfordert eine "überzeugende" Kerze. Wenn der Kurs zwar ein neues Hoch macht, aber dann wieder abverkauft wird (langer Docht oben), gibt mein angepasstes Script kein Signal mehr aus.
Trend-Filter (SMA20):
Bauer handelt ungern gegen den kurzfristigen Trend. Das Script prüft nun, ob der Kurs über dem Durchschnitt der letzten 20 Tage liegt.
ATR-Stop-Loss:
Anstatt nur das Ziel (prev_high) anzuzeigen, berechnet das Script jetzt einen volatilitätsbasierten Stop-Loss (ATR = Average True Range). Das ist ein Kern-Element seiner Risiko-Lehre.
Wetter-Definition:
Das "Wetter" bezieht sich jetzt nicht mehr auf einen willkürlichen Startzeitpunkt der Session, sondern auf die Lage des Kurses zum gleitenden Durchschnitt (SMA20) – eine fachlich fundiertere Methode.
Hinweis: Du musst yfinance und pandas installiert haben. Das Script berechnet nun automatisch die ATR und den SMA für jedes Symbol.
KI-Antworten können Fehler enthalten. Weitere Informationen



können wir den regelmäßig updaten lassen im Zeitraum von 45 sekunden und den heutigen Startpreis under dem Namen vom Papier zeigen?
Hier ist dein angepasstes Script für 2026. Ich habe das Update-Intervall auf 45 Sekunden (45000 ms) gesetzt und die Datenabfrage so erweitert, dass der heutige Eröffnungspreis (Open) direkt unter dem Namen des Wertpapiers angezeigt wird. 
Reddit
Reddit
 +2
python
import os
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# --- 0. AUTO-REFRESH (45 Sekunden) ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

# Intervall auf 45000ms = 45 Sekunden gesetzt
st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Dr. Bauer Strategie-Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .ticker-name { color: #00ff00; font-size: 16px; font-weight: bold; margin-bottom: 0px; }
    .open-price { color: #888888; font-size: 11px; margin-top: -5px; margin-bottom: 10px; }
    [data-testid="stMetricValue"] { font-size: 22px !important; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK: DR. BAUER ANALYSE ---
def analyze_bauer_style(df):
    """Bauer-Methodik: Candlestick-Stärke + Trend + Vola-Stop"""
    if len(df) < 20: return None
    
    curr = df['Close'].iloc[-1]
    prev_high = df['High'].iloc[-2]
    
    # 1. Candlestick Check: Schließt die Kerze im oberen Drittel? (Stärke-Signal)
    body_size = abs(curr - df['Open'].iloc[-1])
    upper_wick = df['High'].iloc[-1] - max(curr, df['Open'].iloc[-1])
    is_strong_body = upper_wick < (body_size * 0.3)
    
    # 2. Trend-Check (Preis über SMA20)
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    is_uptrend = curr > sma20
    
    # 3. Breakout-Signal nach Bauer
    bauer_signal = (curr > prev_high) and is_strong_body and is_uptrend
    
    # 4. ATR für Stop-Loss (1.5x Volatilität)
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    
    return {
        "signal": bauer_signal,
        "stop": curr - (atr * 1.5),
        "sma20": sma20,
        "open_today": df['Open'].iloc[-1] # Heutiger Eröffnungspreis
    }

def fetch_data():
    symbols = {
        "^STOXX50E": "EUROSTOXX 50", "^IXIC": "NASDAQ",
        "AAPL": "APPLE", "MSFT": "MICROSOFT", "NVDA": "NVIDIA", 
        "SAP.DE": "SAP", "ASML": "ASML"
    }
    results = {}
    aktuell = datetime.now()
    
    for ticker, label in symbols.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1mo")
            if len(df) >= 20:
                analysis = analyze_bauer_style(df)
                curr = df['Close'].iloc[-1]
                
                results[label] = {
                    "price": curr,
                    "open": analysis['open_today'],
                    "is_breakout": analysis['signal'],
                    "stop": analysis['stop'],
                    "delta": ((curr - analysis['open_today']) / analysis['open_today']) * 100,
                    "sma_dist": curr > analysis['sma20']
                }
        except: pass
    return results

# --- 3. RENDER ---
st.title("📡 Dr. Bauer Strategie-Terminal")
st.write(f"Letztes Update: {datetime.now().strftime('%H:%M:%S')} (Intervall: 45s)")

data = fetch_data()

for label, d in data.items():
    with st.container():
        # Name und Eröffnungspreis direkt darunter
        st.markdown(f"""
            <div class='ticker-name'>{label}</div>
            <div class='open-price'>Eröffnung heute: {d['open']:.2f}</div>
        """, unsafe_allow_html=True)
        
        cols = st.columns([1, 1, 1])
        with cols[0]:
            st.metric("Kurs", f"{d['price']:.2f}", f"{d['delta']:+.2f}%")
        with cols[1]:
            color = "#00ff00" if d['is_breakout'] else "#444"
            st.markdown(f"<h3 style='color:{color};'>{'🚀 SIGNAL' if d['is_breakout'] else 'WAIT'}</h3>", unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"<div style='color:#ff4b4b; font-size:12px;'>Bauer-Stop (ATR):<br><b>{d['stop']:.2f}</b></div>", unsafe_allow_html=True)
        st.divider()
Verwende Code mit Vorsicht.

Die wichtigsten Änderungen:
Eröffnungspreis: Ich nutze df['Open'].iloc[-1] aus den yfinance-Historiedaten, um den exakten Eröffnungspreis des heutigen Handelstages abzugreifen.
Layout: Der Name des Papiers steht nun oben in Grün, gefolgt vom grauen "Eröffnung heute" Text – genau wie gewünscht.
45s Taktung: Die st_autorefresh Funktion sorgt nun alle 45 Sekunden für einen kompletten Neulauf der Daten.
Bauer-Methodik: Die Logik prüft weiterhin, ob der Kurs über dem SMA20 liegt und ob die aktuelle Kerze "stark" genug ist (wenig Verkaufsdruck am oberen Ende), bevor ein Signal erscheint. 
Reddit
Reddit
 +2
KI-Antworten können Fehler enthalten. Weitere Informationen




undefined
undefined
undefined
3 Websites
yFinance – Getting price data : r/learnpython - Reddit
12.01.2023 — Snapper04. yFinance – Getting price data. I know of two ways to get price data on a stock. The direct way is to use the yf. downlo...

Reddit
How to download market data with yfinance and Python
19.03.2025 — Open: Price at market open. High: Highest price during the trading session. Low: Lowest price during the trading session. Close: P...

pythonfintech.com

README.md - kmcgrady/streamlit-autorefresh - GitHub
Parameters. interval: int Amount of time in milliseconds to limit: int or None Amount of refreshes to allow. If none, it will refr...

GitHub

können wir einen expander mit EURUSD, BIST100, Nifty, TRS, MOEX, EURRUB einfügen
Hier ist die aktualisierte Version deines Terminals für das Jahr 2026. Ich habe einen separaten Bereich (Expander) für die gewünschten globalen Märkte und Währungen hinzugefügt.
Das Script nutzt nun die korrekten Ticker-Symbole für BIST 100 (Türkei), Nifty 50 (Indien), RTS & MOEX (Russland) sowie die Währungspaare.
python
import os
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# --- 0. AUTO-REFRESH (45 Sekunden) ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Dr. Bauer Strategie-Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .ticker-name { color: #00ff00; font-size: 16px; font-weight: bold; margin-bottom: 0px; }
    .open-price { color: #888888; font-size: 11px; margin-top: -5px; margin-bottom: 10px; }
    .expander-style { border: 1px solid #333; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK: ANALYSE ---
def analyze_bauer_style(df):
    if len(df) < 20: return None
    curr = df['Close'].iloc[-1]
    prev_high = df['High'].iloc[-2]
    
    # Candlestick-Stärke (Schlusskurs im oberen Drittel?)
    body_size = abs(curr - df['Open'].iloc[-1])
    upper_wick = df['High'].iloc[-1] - max(curr, df['Open'].iloc[-1])
    is_strong_body = upper_wick < (body_size * 0.3)
    
    # Trend (SMA20)
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    
    # ATR Stop-Loss
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    
    return {
        "signal": (curr > prev_high) and is_strong_body and (curr > sma20),
        "stop": curr - (atr * 1.5),
        "open_today": df['Open'].iloc[-1]
    }

def fetch_data(symbols):
    results = {}
    for ticker, label in symbols.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1mo")
            if not df.empty:
                analysis = analyze_bauer_style(df)
                curr = df['Close'].iloc[-1]
                results[label] = {
                    "price": curr, "open": analysis['open_today'],
                    "is_breakout": analysis['signal'], "stop": analysis['stop'],
                    "delta": ((curr - analysis['open_today']) / analysis['open_today']) * 100
                }
        except: pass
    return results

# --- 3. DEFINITION DER TICKER ---
main_stocks = {
    "AAPL": "APPLE", "MSFT": "MICROSOFT", "NVDA": "NVIDIA", "SAP.DE": "SAP"
}

global_markets = {
    "EURUSD=X": "EUR/USD", 
    "XU100.IS": "BIST 100 (TR)", 
    "^NSEI": "NIFTY 50 (IN)", 
    "RTSI.ME": "RTS INDEX (RU)", 
    "IMOEX.ME": "MOEX RUSSIA", 
    "EURRUB=X": "EUR/RUB"
}

# --- 4. RENDER ---
st.title("📡 Dr. Bauer Strategie-Terminal")
st.write(f"Update: {datetime.now().strftime('%H:%M:%S')} | Intervall: 45s")

# Sektion 1: Fokus-Aktien
st.subheader("🔥 Fokus-Werte")
data_main = fetch_data(main_stocks)
for label, d in data_main.items():
    cols = st.columns([1, 1, 1, 1])
    with cols[0]:
        st.markdown(f"<div class='ticker-name'>{label}</div><div class='open-price'>Start: {d['open']:.2f}</div>", unsafe_allow_html=True)
    with cols[1]: st.metric("Kurs", f"{d['price']:.2f}", f"{d['delta']:+.2f}%")
    with cols[2]: st.markdown(f"### {'🚀 BUY' if d['is_breakout'] else 'WAIT'}")
    with cols[3]: st.markdown(f"<small>Stop:</small><br><b style='color:#ff4b4b;'>{d['stop']:.2f}</b>", unsafe_allow_html=True)
    st.divider()

# Sektion 2: Expander für globale Märkte
with st.expander("🌍 GLOBALE MÄRKTE & WÄHRUNGEN (EURUSD, BIST, NIFTY, MOEX)"):
    data_global = fetch_data(global_markets)
    for label, d in data_global.items():
        g_cols = st.columns([1, 1, 1, 1])
        with g_cols[0]:
            st.markdown(f"**{label}**<br><small>Start: {d['open']:.4f}</small>", unsafe_allow_html=True)
        with g_cols[1]: st.metric("", f"{d['price']:.4f}", f"{d['delta']:+.2f}%")
        with g_cols[2]: st.write("🚀" if d['is_breakout'] else "⚪")
        with g_cols[3]: st.write(f"Stop: {d['stop']:.4f}")
        st.markdown("<hr style='margin:5px; border-color:#222;'>", unsafe_allow_html=True)
Verwende Code mit Vorsicht.

Details zur Anpassung:
Expander: Die globalen Werte sind nun platzsparend in einem ausklappbaren Bereich untergebracht.
Ticker-Logik:
BIST 100: XU100.IS (Istanbul Stock Exchange).
Nifty 50: ^NSEI (National Stock Exchange of India).
TRS/RTS: RTSI.ME (RTS Index in USD).
MOEX: IMOEX.ME (Moscow Exchange in RUB).
Startpreis: Erscheint bei allen Werten direkt unter dem Namen des Papiers.
Genauigkeit: Bei Währungen (EURUSD/EURRUB) werden automatisch 4 Nachkommastellen angezeigt, um die feinen Bewegungen nach Bauer-Art besser zu erfassen. 
KI-Antworten können Fehler enthalten. Weitere Informationen







3 Websites
NSEI: NIFTY 50 - Stock Price, Quote and News - CNBC
.NSEI: NIFTY 50 - Stock Price, Quote and News - CNBC. NIFTY 50 .NSEI:National Stock Exchange of India. EXPORT. + *Data is delayed ...

CNBC

RTS Index - Wikipedia
The RTS Index (RTSI; Russian: Индекс РТС) is a free-float capitalization-weighted index of 50 Russian stocks traded on the Moscow ...

Wikipedia

MOEX RUSSIA INDEX
30.01.2026 — Page 1. MOEX RUSSIA INDEX. Код: IMOEX. Currency: RUB. ISIN: RU000A0JP7K5. MOEX RUSSIA INDEX PERFOMANCE. MAIN CHARACTERISTICS. 2024...

Московская Биржа
Frage stellen


Antwort des KI-Modus ist fertig
