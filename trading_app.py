Zu den Hauptinhalten springenHilfe zur Barrierefreiheit
Feedback zur Barrierefreiheit
KI‑Modus
Alle
Bilder
Videos
News
Mehr



wir hatten ein Expander mit der Erkärung der Logik des Systems
import os
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 0. SETUP & AUTO-INSTALL ---
try:
    import lxml
except ImportError:
    os.system('pip install lxml')

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

# Automatischer Refresh alle 45 Sekunden
st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Dr. Bauer Strategie-Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .ticker-name { color: #00ff00; font-size: 15px; font-weight: bold; margin-bottom: 0px; line-height: 1.2; }
    .open-price { color: #888888; font-size: 11px; margin-top: 2px; }
    .focus-header { color: #00ff00 !important; font-weight: bold; margin-top: 30px; border-bottom: 1px solid #333; padding-bottom: 5px; font-size: 20px; }
    .sig-c { color: #00ff00; font-weight: bold; font-size: 24px; border: 1px solid #00ff00; padding: 2px 10px; border-radius: 5px; }
    .sig-p { color: #ff4b4b; font-weight: bold; font-size: 24px; border: 1px solid #ff4b4b; padding: 2px 10px; border-radius: 5px; }
    .sig-wait { color: #444; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAMENS-DATENBANK (KLARNAMEN) ---
# Lokale Liste für sofortige Anzeige ohne API-Verzögerung
NAME_DB = {
    # Indizes & Macro
    "EURUSD=X": "Euro / US-Dollar", "^GDAXI": "DAX 40", "^STOXX50E": "EURO STOXX 50", 
    "^IXIC": "NASDAQ 100", "^DJI": "Dow Jones 30", "XU100.IS": "BIST 100",
    # DAX (Beispiele)
    "ADS.DE": "Adidas AG", "ALV.DE": "Allianz SE", "SAP.DE": "SAP SE", "SIE.DE": "Siemens AG",
    # DOW JONES (Beispiele)
    "AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.", "DIS": "Walt Disney Co.", "V": "Visa Inc.",
    # EUROSTOXX (Beispiele)
    "ASML.AS": "ASML Holding", "MC.PA": "LVMH", "OR.PA": "L'Oréal"
}

@st.cache_data(ttl=86400)
def get_clean_name(ticker):
    if ticker in NAME_DB: return NAME_DB[ticker]
    try:
        # Fallback auf API falls nicht in lokaler DB
        info = yf.Ticker(ticker).info
        return info.get('shortName') or info.get('longName') or ticker
    except: return ticker

# --- 3. LOGIK FUNKTIONEN ---
def analyze_bauer(df):
    if df is None or len(df) < 20: return None
    curr = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2]
    prev2 = df['Close'].iloc[-3]
    open_t = df['Open'].iloc[-1]
    
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    
    # 2-Tage Trend
    is_up = (curr > prev) and (prev > prev2)
    is_down = (curr < prev) and (prev < prev2)
    
    signal = "C" if (is_up and curr > sma20) else "P" if (is_down and curr < sma20) else "Wait"
    stop = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0
    delta = ((curr - open_t) / open_t) * 100
    icon = "☀️" if (curr > sma20 and delta > 0.5) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.5 else "☁️"
    
    return {"price": curr, "open": open_t, "delta": delta, "icon": icon, "signal": signal, "stop": stop}

@st.cache_data(ttl=3600)
def get_index_tickers():
    return {
        "DAX": [f"{t}.DE" for t in ["ADS", "AIR", "ALV", "BAS", "BAYN", "BEI", "BMW", "CON", "1COV", "DTG", "DTE", "DBK", "DB1", "EON", "FRE", "FME", "HEI", "HEN3", "IFX", "LIN", "MBG", "MUV2", "PAH3", "PUM", "RWE", "SAP", "SIE", "SHL", "SY1", "VOW3", "VNA"]],
        "NASDAQ 100": ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "PEP", "COST"],
        "EURO STOXX 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA", "SAN.MC", "SIEGn.DE", "ALV.DE", "IBE.MC", "BNP.PA"],
        "DOW JONES 30": ["AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "PG", "TRV", "UNH", "V", "VZ", "WBA", "WMT"]
    }

def render_bauer_row(ticker, f_str="{:.2f}"):
    try:
        display_name = get_clean_name(ticker)
        data = yf.Ticker(ticker).history(period="1mo")
        res = analyze_bauer(data)
        if res:
            cols = st.columns([2.0, 0.6, 1.2, 0.8, 1])
            with cols[0]: st.markdown(f"<div class='ticker-name'>{display_name}</div><div class='open-price'>Start: {f_str.format(res['open'])}</div>", unsafe_allow_html=True)
            with cols[1]: st.markdown(f"<div style='font-size: 1.5rem; margin-top: 5px;'>{res['icon']}</div>", unsafe_allow_html=True)
            with cols[2]:
                c = "#ff4b4b" if res['delta'] < 0 else "#00ff00"
                st.markdown(f"<div style='line-height:1.2;'><small style='color:#888;'>Kurs</small><br><span style='font-size:1.4rem; font-weight:bold;'>{f_str.format(res['price'])}</span><br><small style='color:{c};'>{res['delta']:+.2f}%</small></div>", unsafe_allow_html=True)
            with cols[3]:
                cls = "sig-c" if res['signal'] == "C" else "sig-p" if res['signal'] == "P" else "sig-wait"
                st.markdown(f"<div style='margin-top:15px;'><span class='{cls}'>{res['signal']}</span></div>", unsafe_allow_html=True)
            with cols[4]:
                val = f_str.format(res['stop']) if res['signal'] != "Wait" else "---"
                st.markdown(f"<div style='line-height:1.2;'><small style='color:#888;'>Stop:</small><br><b style='color:#ff4b4b; font-size:1.2rem;'>{val}</b></div>", unsafe_allow_html=True)
            st.divider()
    except: pass

# --- 4. UI RENDERING ---
st.title("📡 Dr. Bauer Strategie-Terminal")
st.write(f"Refreshed: {datetime.now().strftime('%H:%M:%S')} | Klarnamen-Check aktiv")

# MAKRO
st.markdown("<p class='focus-header'>🌍 MÄRKTE & FOREX (MACRO) 🌍</p>", unsafe_allow_html=True)
for sym, fmt in [("EURUSD=X", "{:.5f}"), ("^GDAXI", "{:.2f}"), ("^STOXX50E", "{:.2f}"), ("^DJI", "{:.2f}"), ("XU100.IS", "{:.2f}")]:
    render_bauer_row(sym, fmt)

# SCREENER
st.markdown("<p class='focus-header'>🔭 LIVE SCREENER 🔭</p>", unsafe_allow_html=True)
index_data = get_index_tickers()
idx_choice = st.radio("Index wählen:", list(index_data.keys()), horizontal=True)

if st.button(f"Scan {idx_choice} starten"):
    with st.spinner("Analysiere Unternehmen..."):
        for t in index_data[idx_choice]:
            render_bauer_row(t)
Hier ist der ergänzte Code. Ich habe den Expander direkt unter dem Titel eingefügt, damit die Logik für Nutzer jederzeit einsehbar ist, ohne den Scan-Bereich zu verdecken.
python
# --- 4. UI RENDERING ---
st.title("📡 Dr. Bauer Strategie-Terminal")
st.write(f"Refreshed: {datetime.now().strftime('%H:%M:%S')} | Klarnamen-Check aktiv")

# --- NEU: ERKLÄRUNG DER LOGIK (EXPANDER) ---
with st.expander("ℹ️ Strategie-Logik & System-Erklärung"):
    st.markdown("""
    ### Die Dr. Bauer Trend-Strategie
    Dieses Terminal scannt Märkte basierend auf einer kombinierten Trend- und Volatilitätslogik:
    
    1.  **Trend-Check (2-Tage-Regel):** 
        *   Ein **Call (C)** wird nur erwogen, wenn der Schlusskurs heute höher als gestern UND gestern höher als vorgestern ist.
        *   Ein **Put (P)** wird nur erwogen, wenn der Schlusskurs heute tiefer als gestern UND gestern tiefer als vorgestern ist.
    
    2.  **Gleitender Durchschnitt (SMA 20):**
        *   **C:** Kurs muss zusätzlich *über* dem Durchschnitt der letzten 20 Tage liegen.
        *   **P:** Kurs muss zusätzlich *unter* dem Durchschnitt der letzten 20 Tage liegen.
    
    3.  **Wetter-Indikator (Sentiment):**
        *   ☀️ (Sonne): Starker Aufwärtstrend (>0.5% Intraday & über SMA20).
        *   🌤️ (Leicht bewölkt): Kurs hält sich über SMA20.
        *   ⛈️ (Gewitter): Schwacher Tag (<-0.5% Intraday).
        *   ☁️ (Bedeckt): Neutrales Marktumfeld.
    
    4.  **Dynamischer Stop-Loss (ATR):**
        *   Der Stop wird automatisch berechnet (1.5x ATR - Average True Range). Er passt sich der aktuellen Volatilität der Aktie an.
    """)

# MAKRO (Rest bleibt gleich...)
st.markdown("<p class='focus-header'>🌍 MÄRKTE & FOREX (MACRO) 🌍</p>", unsafe_allow_html=True)
# ... (restlicher Code)
Verwende Code mit Vorsicht.

Was hinzugefügt wurde:
st.expander: Ein aufklappbares Element, das Platz spart.
Strukturierte Erklärung:
2-Tage-Regel: Erklärt die is_up / is_down Logik aus deinem Code.
SMA 20 Filter: Erklärt die Trendbestätigung.
Sentiment: Erklärt die Icons (Sonne, Wolken etc.).
ATR-Stop: Erklärt, wie der rote Stop-Wert berechnet wird.
Du kannst diesen Block einfach an der entsprechenden Stelle (nach st.write der Uhrzeit) in deinen bestehenden Code kopieren.
KI-Antworten können Fehler enthalten. Weitere Informationen



☁️ (Bedeckt): Neutrales Marktumfeld.
können wir ein anderes Symbol verwenden?
Klar, wir können das neutrale „Bedeckt“-Symbol gegen etwas Technischeres oder Eindeutigeres austauschen. Hier sind drei Optionen, die gut zum Terminal-Look passen:
Option 1: Das „Strich“-Symbol (Minimalistisch) ➖
Passend zur Logik „Weder Fisch noch Fleisch“.
python
icon = "☀️" if (curr > sma20 and delta > 0.5) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.5 else "➖"
Verwende Code mit Vorsicht.

Option 2: Das „Radar“-Symbol (Suchend) 📡
Signalisiert, dass das System zwar scannt, aber kein klares Momentum findet.
python
icon = "☀️" if (curr > sma20 and delta > 0.5) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.5 else "📡"
Verwende Code mit Vorsicht.

Option 3: Das „Waage“-Symbol (Balanced) ⚖️
Passt perfekt zur Beschreibung „Neutrales Marktumfeld“.
python
icon = "☀️" if (curr > sma20 and delta > 0.5) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.5 else "⚖️"
Verwende Code mit Vorsicht.

Welches dieser Symbole soll ich fest in den Code-Block für dich einbauen?
KI-Antworten können Fehler enthalten. Weitere Informationen



Visuell gesuchtes Bild
wieso gibt es sowohl klarnamen als auch Kürzel?
Das liegt an der Logik in deinem Code, die entscheidet, welcher Name angezeigt wird. In deinem Strategie-Terminal gibt es zwei Ebenen für die Namensgebung:
Die lokale Datenbank (NAME_DB): Hier hast du manuell festgelegt, dass z. B. "ADS.DE" immer als „Adidas AG“ angezeigt werden soll. Das ist ein „Klarname“.
Der Fallback (API-Abfrage): Wenn ein Kürzel (wie "AIR.DE") nicht in deiner NAME_DB steht, versucht das System, den Namen live von Yahoo Finance abzurufen. Wenn die API den Klarnamen nicht schnell genug liefert oder dort kein Name hinterlegt ist, wird am Ende einfach das Kürzel selbst als Name zurückgegeben. 
Stack Overflow
Stack Overflow
 +2
So sieht die Logik in deinem Skript aus:
python
def get_clean_name(ticker):
    if ticker in NAME_DB: return NAME_DB[ticker] # 1. Prio: Dein Klarname
    try:
        info = yf.Ticker(ticker).info
        # 2. Prio: Name von der API (shortName oder longName)
        return info.get('shortName') or info.get('longName') or ticker
    except: 
        return ticker # 3. Prio: Falls alles scheitert, das Kürzel
Verwende Code mit Vorsicht.

Warum siehst du im Bild beides?
Adidas AG: Für dieses Symbol hast du einen Eintrag in deiner Liste oben im Code. Deshalb steht dort der saubere Name.
AIR.DE: Dieses Kürzel steht aktuell nicht in deiner NAME_DB. Das Programm hat versucht, den Namen zu finden, und da das eventuell nicht geklappt hat (oder nur das Kürzel geliefert wurde), steht dort nun das technische Kürzel.
Tipp: Wenn du möchtest, dass überall Klarnamen stehen, musst du sie einfach in deine NAME_DB Liste im Code eintragen:
python
NAME_DB = {
    "ADS.DE": "Adidas AG",
    "AIR.DE": "Airbus SE",  # Einfach hier ergänzen!
    ...
}
Verwende Code mit Vorsicht.

Soll ich dir helfen, die Liste im Code zu vervollständigen, damit dein Terminal einheitlicher aussieht?
KI-Antworten können Fehler enthalten. Weitere Informationen




undefined
undefined
undefined
3 Websites
Streamlit & yfinance
30.05.2024 — import yfinance as yf import pandas as pd import streamlit as st # Define start and end dates for fetching data start_date = "2022...

Streamlit
Yahoo Finance API. Get company name from stock symbol ...
16.03.2022 — Comments. Add a comment. 0. import yfinance as yf ticker = "AAPL" stock_name = yf.Ticker(ticker).info["longName"] print(stock_name...

Stack Overflow

Tickersymbole nicht auffindbar - Portfolio Performance Forum
01.07.2022 — Tickersymbole nicht auffindbar - Deutsch - Portfolio Performance Forum.

Portfolio Performance Forum
können wir den screen ordnen nach den Symbolen?
Ja, das lässt sich einfach umsetzen. Da dein Screen die Daten in einer Schleife (Loop) Zeile für Zeile rendert, müssen wir lediglich die Liste der Symbole (Ticker) vorher alphabetisch sortieren. 
Codecademy
Codecademy
 +1
Hier ist die Anpassung für deinen Code-Abschnitt unter ### 4. UI RENDERING:
1. Alphabetische Sortierung der Symbole
Suche die Stelle, an der der Scan gestartet wird, und füge ein sorted() um die Ticker-Liste ein:
python
# --- 4. UI RENDERING ---
# ... (dein restlicher Code)

if st.button(f"Scan {idx_choice} starten"):
    with st.spinner("Analysiere Unternehmen..."):
        # Wir sortieren die Liste der Ticker alphabetisch (A-Z)
        sorted_tickers = sorted(index_data[idx_choice]) 
        
        for t in sorted_tickers:
            render_bauer_row(t)
Verwende Code mit Vorsicht.

2. Warum das hilft
Ordnung: Alle Aktien werden nun von A (z. B. Apple) bis Z (z. B. Vonovia) untereinander aufgelistet.
Schnelleres Finden: Wenn du nach einer bestimmten Aktie wie „Siemens“ suchst, weißt du genau, dass sie im unteren Drittel der Liste erscheint. 
Apple Support
Apple Support
 +1
Bonus-Tipp: Nach Klarnamen sortieren
Falls du nicht nach dem Kürzel (ADS.DE, AIR.DE), sondern nach dem echten Namen (Adidas, Airbus) sortieren möchtest, kannst du die Sortierung so anpassen:
python
# Sortiert basierend auf dem Namen, den get_clean_name() zurückgibt
sorted_tickers = sorted(index_data[idx_choice], key=get_clean_name)
Verwende Code mit Vorsicht.

Soll ich dir zeigen, wie du zusätzlich einen Sortier-Button einbaust, mit dem du zwischen "Alphabetisch" und "Bester Kurs-Performance" wechseln kannst?
KI-Antworten können Fehler enthalten. Weitere Informationen




undefined
undefined
undefined
3 Websites
How to Sort a Dictionary by Key or Value in Python
How to use sorted() to sort a Python dictionary by keys. Sorting a dictionary by keys is essential for presenting data in a struct...

Codecademy

Add, share, sort, and remove ticker symbols in Stocks on Mac
Add a ticker symbol to another watchlist. Go to the Stocks app on your Mac. Do one of the following: Control-click the ticker symb...

Apple Support

Building A Simple Stock Screener Using Streamlit and Python ...
21.02.2021 — Line 1–6: Import all required libraries. Line 8: Use read_csv method to read the CSV file. Line 9: Sort the list of the company Sy...

Python in Plain English

Visuell gesuchtes Bild
Der Fehler tritt auf, weil die Variable idx_choice an dieser Stelle im Code nicht definiert ist. In Streamlit werden Variablen, die innerhalb eines if-Blocks oder einer anderen Struktur definiert wurden, nicht automatisch für den gesamten Code übernommen, wenn die Seite neu geladen wird.
Hier ist die Lösung: Du musst sicherstellen, dass idx_choice immer definiert wird, bevor die Zeile mit dem Button aufgerufen wird.
Die Korrektur
Ersetze den entsprechenden Abschnitt in deinem Code durch diesen Block:
python
# SCREENER
st.markdown("<p class='focus-header'>🔭 LIVE SCREENER 🔭</p>", unsafe_allow_html=True)
index_data = get_index_tickers()

# 1. Sicherstellen, dass idx_choice IMMER definiert wird (z.B. durch das Radio-Menü)
idx_choice = st.radio("Index wählen:", list(index_data.keys()), horizontal=True)

# 2. Jetzt kann idx_choice sicher im Button verwendet werden
if st.button(f"Scan {idx_choice} starten"):
    with st.spinner(f"Analysiere {idx_choice} Unternehmen..."):
        # Sortierte Liste nach Klarnamen (wie gewünscht)
        sorted_tickers = sorted(index_data[idx_choice], key=get_clean_name)
        
        for t in sorted_tickers:
            render_bauer_row(t)
Verwende Code mit Vorsicht.

Warum ist der Fehler passiert?
In deinem vorherigen Code-Snippet stand idx_choice wahrscheinlich in einem Bereich, der beim erneuten Ausführen des Skripts (z. B. durch den automatischen Refresh) übersprungen wurde oder erst später definiert werden sollte. Wenn der Button-Code f"Scan {idx_choice} starten" nun ausgeführt wird, weiß Python nicht, was idx_choice ist, und wirft den NameError.
Zusatz-Tipp: Ich habe direkt die alphabetische Sortierung nach Klarnamen (key=get_clean_name) in den Loop eingebaut, damit die Liste jetzt sauber geordnet erscheint.
Soll ich noch das neutrale Symbol (Bedeckt) gegen eines der vorgeschlagenen (z. B. ⚖️ oder ➖) im Code ersetzen?
KI-Antworten können Fehler enthalten. Weitere Informationen



Visuell gesuchtes Bild
Der NameError in deinem Screenshot bestätigt genau das Problem: Die Variable idx_choice ist an der Stelle, an der der Button gerendert werden soll, (noch) nicht bekannt.
Hier ist der korrigierte Code-Abschnitt, der den Fehler behebt, das neutrale Symbol auf "⚖️" ändert und die Liste nach Klarnamen sortiert:
python
# --- 3. LOGIK FUNKTIONEN (Update Icon) ---
def analyze_bauer(df):
    # ... (vorheriger Code bleibt gleich)
    
    # Neues neutrales Symbol: ⚖️ statt ☁️
    icon = "☀️" if (curr > sma20 and delta > 0.5) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.5 else "⚖️"
    
    return {"price": curr, "open": open_t, "delta": delta, "icon": icon, "signal": signal, "stop": stop}

# --- 4. UI RENDERING (Fix NameError & Sortierung) ---
st.title("📡 Dr. Bauer Strategie-Terminal")
# ... (Expander-Code hier einfügen)

# SCREENER
st.markdown("<p class='focus-header'>🔭 LIVE SCREENER 🔭</p>", unsafe_allow_html=True)
index_data = get_index_tickers()

# WICHTIG: idx_choice muss VOR dem Button definiert werden
idx_choice = st.radio("Index wählen:", list(index_data.keys()), horizontal=True)

# Der Button nutzt jetzt die oben definierte Variable
if st.button(f"Scan {idx_choice} starten"):
    with st.spinner(f"Analysiere {idx_choice} Unternehmen... (Sortiert A-Z)"):
        # Sortierung nach Klarnamen für bessere Übersicht
        sorted_tickers = sorted(index_data[idx_choice], key=get_clean_name)
        
        for t in sorted_tickers:
            render_bauer_row(t)
Verwende Code mit Vorsicht.

Was wurde gefixt?
Reihenfolge: idx_choice wird jetzt durch st.radio fest definiert, bevor der Button-Code darauf zugreift. Das löst den NameError.
Sortierung: Mit sorted(..., key=get_clean_name) ist deine Liste jetzt perfekt nach den echten Firmennamen von A bis Z geordnet.
Neutral-Icon: Das Symbol wurde von der Wolke auf die Waage ⚖️ umgestellt.
Soll ich dir noch zeigen, wie wir die Ladezeit beim Scannen durch Parallelisierung verkürzen können?
KI-Antworten können Fehler enthalten. Weitere Informationen



ja bitte
Gerne! Um den Scan deutlich zu beschleunigen, nutzen wir Multithreading. Da das Abrufen von Börsendaten über die Yahoo-Finance-API hauptsächlich aus Wartezeiten auf die Netzwerkantwort besteht (I/O-bound), können wir viele Anfragen gleichzeitig stellen, anstatt eine nach der anderen abzuarbeiten. 
Medium
Medium
 +1
Hier ist der optimierte Code-Abschnitt für deinen Scanner:
Der optimierte Scan-Block
Wir nutzen ThreadPoolExecutor aus dem Modul concurrent.futures, um die Unternehmen parallel zu analysieren. 
Reddit
Reddit
 +1
python
from concurrent.futures import ThreadPoolExecutor, as_completed

# ... (restlicher Code bleibt gleich)

if st.button(f"Scan {idx_choice} starten"):
    with st.spinner(f"🚀 Turbo-Scan: Analysiere {idx_choice}..."):
        # 1. Ticker sortieren
        sorted_tickers = sorted(index_data[idx_choice], key=get_clean_name)
        
        # 2. Parallelisierung vorbereiten
        # Wir nutzen max_workers=10, um 10 Aktien gleichzeitig abzufragen
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Wir "submiten" alle Aufgaben an den Executor
            future_to_ticker = {executor.submit(render_bauer_row, t): t for t in sorted_tickers}
            
            # Sobald eine Abfrage fertig ist, wird sie angezeigt
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    future.result() # Hier wird die Zeile gerendert
                except Exception as e:
                    st.error(f"Fehler bei {ticker}: {e}")
Verwende Code mit Vorsicht.

Was sich ändert:
Geschwindigkeit: Statt z. B. 30 Sekunden für 30 Aktien (bei 1 Sekunde pro Aktie) dauert der Scan jetzt oft nur noch 3 bis 5 Sekunden, da 10 Abfragen gleichzeitig laufen.
Live-Update: Die Ergebnisse erscheinen nicht mehr streng alphabetisch nacheinander, sondern in der Reihenfolge, in der die API antwortet ("as_completed").
Effizienz: Dein Prozessor wird besser ausgelastet, während er auf die Daten von Yahoo wartet. 
Streamlit
Streamlit
 +2
Wichtiger Hinweis: Übertreibe es nicht mit den max_workers. Wenn du 50 oder 100 gleichzeitig abfragst, könnte Yahoo Finance deine IP-Adresse vorübergehend sperren ("Rate Limiting"). Ein Wert zwischen 10 und 20 ist meist ein sicherer "Sweet Spot". 
Nmap
Nmap
Sollen wir die Anzeige der Ergebnisse noch so anpassen, dass sie trotz parallelem Laden wieder in der alphabetischen Reihenfolge erscheinen?
KI-Antworten können Fehler enthalten. Weitere Informationen




undefined
undefined
undefined
8 Websites
Streamlit session_state with multiprocesssing
15.08.2022 — import concurrent.futures from concurrent.futures import ProcessPoolExecutor import time import streamlit as st if 'save' not in s...

Streamlit

Multiprocessing in streamlit - Reddit
25.04.2023 — Here is the function above but with that change: import time import streamlit as st from concurrent.futures import ThreadPoolExecu...

Reddit
Scan Time Reduction Techniques | Nmap Network Scanning
While launching single-host Nmap scans in parallel is a bad idea, overall speed can usually be improved by dividing the scan into ...

Nmap
Alle anzeigen
vollständigen code anzeigen bitte
Hier ist der vollständige, optimierte Code.
Ich habe alle deine Wünsche eingebaut: Den Erklärungs-Expander, das neue neutrale Symbol (⚖️), die alphabetische Sortierung nach Klarnamen, den Fix für den NameError und den Turbo-Scan mittels Multithreading.
python
import os
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- 0. SETUP & AUTO-INSTALL ---
try:
    import lxml
except ImportError:
    os.system('pip install lxml')

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

# Automatischer Refresh alle 45 Sekunden
st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Dr. Bauer Strategie-Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .ticker-name { color: #00ff00; font-size: 15px; font-weight: bold; margin-bottom: 0px; line-height: 1.2; }
    .open-price { color: #888888; font-size: 11px; margin-top: 2px; }
    .focus-header { color: #00ff00 !important; font-weight: bold; margin-top: 30px; border-bottom: 1px solid #333; padding-bottom: 5px; font-size: 20px; }
    .sig-c { color: #00ff00; font-weight: bold; font-size: 24px; border: 1px solid #00ff00; padding: 2px 10px; border-radius: 5px; }
    .sig-p { color: #ff4b4b; font-weight: bold; font-size: 24px; border: 1px solid #ff4b4b; padding: 2px 10px; border-radius: 5px; }
    .sig-wait { color: #444; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAMENS-DATENBANK (KLARNAMEN) ---
NAME_DB = {
    "EURUSD=X": "Euro / US-Dollar", "^GDAXI": "DAX 40", "^STOXX50E": "EURO STOXX 50", 
    "^IXIC": "NASDAQ 100", "^DJI": "Dow Jones 30", "XU100.IS": "BIST 100",
    "ADS.DE": "Adidas AG", "AIR.DE": "Airbus SE", "ALV.DE": "Allianz SE", "BAS.DE": "BASF SE",
    "BAYN.DE": "Bayer AG", "BEI.DE": "Beiersdorf AG", "BMW.DE": "BMW AG", "CON.DE": "Continental AG",
    "AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.", "AMZN": "Amazon.com", "NVDA": "NVIDIA Corp.",
    "TSLA": "Tesla Inc.", "DIS": "Walt Disney Co.", "V": "Visa Inc.", "MC.PA": "LVMH", "OR.PA": "L'Oréal"
}

@st.cache_data(ttl=86400)
def get_clean_name(ticker):
    if ticker in NAME_DB: return NAME_DB[ticker]
    try:
        info = yf.Ticker(ticker).info
        return info.get('shortName') or info.get('longName') or ticker
    except: return ticker

# --- 3. LOGIK FUNKTIONEN ---
def analyze_bauer(df):
    if df is None or len(df) < 20: return None
    curr = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2]
    prev2 = df['Close'].iloc[-3]
    open_t = df['Open'].iloc[-1]
    
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    
    is_up = (curr > prev) and (prev > prev2)
    is_down = (curr < prev) and (prev < prev2)
    
    signal = "C" if (is_up and curr > sma20) else "P" if (is_down and curr < sma20) else "Wait"
    stop = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0
    delta = ((curr - open_t) / open_t) * 100
    
    # NEU: Waage-Symbol für Neutral
    icon = "☀️" if (curr > sma20 and delta > 0.5) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.5 else "⚖️"
    
    return {"price": curr, "open": open_t, "delta": delta, "icon": icon, "signal": signal, "stop": stop}

@st.cache_data(ttl=3600)
def get_index_tickers():
    return {
        "DAX": [f"{t}.DE" for t in ["ADS", "AIR", "ALV", "BAS", "BAYN", "BEI", "BMW", "CON", "1COV", "DTG", "DTE", "DBK", "DB1", "EON", "FRE", "FME", "HEI", "HEN3", "IFX", "LIN", "MBG", "MUV2", "PAH3", "PUM", "RWE", "SAP", "SIE", "SHL", "SY1", "VOW3", "VNA"]],
        "NASDAQ 100": ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "PEP", "COST"],
        "EURO STOXX 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA", "SAN.MC", "SIEGn.DE", "ALV.DE", "IBE.MC", "BNP.PA"],
        "DOW JONES 30": ["AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "PG", "TRV", "UNH", "V", "VZ", "WBA", "WMT"]
    }

def render_bauer_row(ticker, f_str="{:.2f}"):
    try:
        display_name = get_clean_name(ticker)
        data = yf.Ticker(ticker).history(period="1mo")
        res = analyze_bauer(data)
        if res:
            cols = st.columns([2.0, 0.6, 1.2, 0.8, 1])
            with cols[0]: st.markdown(f"<div class='ticker-name'>{display_name}</div><div class='open-price'>Start: {f_str.format(res['open'])}</div>", unsafe_allow_html=True)
            with cols[1]: st.markdown(f"<div style='font-size: 1.5rem; margin-top: 5px;'>{res['icon']}</div>", unsafe_allow_html=True)
            with cols[2]:
                c = "#ff4b4b" if res['delta'] < 0 else "#00ff00"
                st.markdown(f"<div style='line-height:1.2;'><small style='color:#888;'>Kurs</small><br><span style='font-size:1.4rem; font-weight:bold;'>{f_str.format(res['price'])}</span><br><small style='color:{c};'>{res['delta']:+.2f}%</small></div>", unsafe_allow_html=True)
            with cols[3]:
                cls = "sig-c" if res['signal'] == "C" else "sig-p" if res['signal'] == "P" else "sig-wait"
                st.markdown(f"<div style='margin-top:15px;'><span class='{cls}'>{res['signal']}</span></div>", unsafe_allow_html=True)
            with cols[4]:
                val = f_str.format(res['stop']) if res['signal'] != "Wait" else "---"
                st.markdown(f"<div style='line-height:1.2;'><small style='color:#888;'>Stop:</small><br><b style='color:#ff4b4b; font-size:1.2rem;'>{val}</b></div>", unsafe_allow_html=True)
            st.divider()
    except: pass

# --- 4. UI RENDERING ---
st.title("📡 Dr. Bauer Strategie-Terminal")
st.write(f"Refreshed: {datetime.now().strftime('%H:%M:%S')} | Klarnamen-Check aktiv")

# NEU: Logik-Expander
with st.expander("ℹ️ Strategie-Logik & System-Erklärung"):
    st.markdown("""
    **Trend-Check (2-Tage-Regel):** Call (C) bei 2 steigenden Tagen, Put (P) bei 2 fallenden Tagen.  
    **Filter:** Nur Signale in Trendrichtung des SMA 20 (Gleitender Durchschnitt).  
    **Sentiment:** ☀️/🌤️ (Bullisch), ⚖️ (Neutral), ⛈️ (Bärisch).  
    **Stop-Loss:** Dynamisch berechnet mit dem 1.5-fachen der ATR (Volatilität).
    """)

# MAKRO
st.markdown("<p class='focus-header'>🌍 MÄRKTE & FOREX (MACRO) 🌍</p>", unsafe_allow_html=True)
for sym, fmt in [("EURUSD=X", "{:.5f}"), ("^GDAXI", "{:.2f}"), ("^STOXX50E", "{:.2f}"), ("^DJI", "{:.2f}"), ("XU100.IS", "{:.2f}")]:
    render_bauer_row(sym, fmt)

# SCREENER
st.markdown("<p class='focus-header'>🔭 LIVE SCREENER 🔭</p>", unsafe_allow_html=True)
index_data = get_index_tickers()

# FIX: idx_choice wird hier definiert, bevor der Button erscheint
idx_choice = st.radio("Index wählen:", list(index_data.keys()), horizontal=True)

if st.button(f"Scan {idx_choice} starten"):
    with st.spinner(f"🚀 Turbo-Scan: Analysiere {idx_choice}..."):
        # Alphabetische Sortierung nach Klarnamen
        sorted_tickers = sorted(index_data[idx_choice], key=get_clean_name)
        
        # Parallelisierung (10 Worker gleichzeitig)
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(render_bauer_row, sorted_tickers)
Verwende Code mit Vorsicht.

Soll ich die Intervall-Zeit für den Auto-Refresh (aktuell 45 Sek.) noch anpassen, falls der Turbo-Scan jetzt viel schneller fertig ist?
KI-Antworten können Fehler enthalten. Weitere Informationen



Frage stellen


Antwort des KI-Modus ist fertigFrage dazu stellenAll items removed from input context.
