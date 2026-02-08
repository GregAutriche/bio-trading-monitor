import pandas as pd
from datetime import datetime, timedelta

# 1. Daten-Vorbereitung (Simulierte Datenbank)
# Hier halten wir die Champions der letzten 20 Tage fest.
# In deiner App würde dies aus einer CSV oder SQL-Datenbank geladen.
def get_historical_champions():
    # Beispielhafte Daten für Ungarn (.BU), Bulgarien (.SO) und DAX (.DE)
    # Format: { Datum: [Liste der Ticker] }
    history = {}
    today = datetime.now()
    for i in range(20):
        date_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        # Beispiel-Daten füllen
        if i % 2 == 0:
            history[date_str] = ["SAP.DE", "MOL.BU", "OTP.BU", "A1.VI"]
        else:
            history[date_str] = ["SAP.DE", "IFX.DE", "MOL.BU"]
    return history

# 2. Logik: Häufigkeit & Ranking berechnen
def calculate_champion_ranking():
    history = get_historical_champions()
    all_tickers = []
    for day_tickers in history.values():
        all_tickers.extend(day_tickers)
    
    # In Pandas DataFrame umwandeln für einfache Analyse
    df = pd.DataFrame(all_tickers, columns=['ticker'])
    ranking = df['ticker'].value_counts().reset_index()
    ranking.columns = ['ticker', 'count']
    
    # Sortierung nach Häufigkeit ist durch value_counts() bereits gegeben
    return ranking.to_dict(orient='records')

# 3. HTML-Generator für den Slider
def generate_slider_html(champions_ranking):
    # CSS für den horizontalen Slider
    html = """
    <style>
        .champion-slider {
            display: flex;
            overflow-x: auto;
            gap: 15px;
            padding: 20px;
            background: #1a1a1a; /* Dunkles Design passend zur App */
            border-radius: 12px;
        }
        .champion-card {
            min-width: 140px;
            background: #2d2d2d;
            color: white;
            padding: 15px;
            border-radius: 8px;
            border-bottom: 4px solid #555;
            flex-shrink: 0;
            text-align: center;
        }
        .count-badge { font-size: 0.9em; color: #aaa; }
        .status-low { border-color: #28a745; } /* <10% - Grün */
        .status-high { border-color: #dc3545; } /* >90% - Rot */
    </style>
    <div class="champion-slider">
    """
    
    for item in champions_ranking:
        ticker = item['ticker']
        count = item['count']
        
        # Hier die Logik für deine 10/90-Regel einbauen (Beispielwert)
        # Nehmen wir an, wir rufen hier den aktuellen Kurs ab:
        current_level = 95 # Beispielwert in %
        
        status_class = ""
        status_text = "Normal"
        if current_level > 90:
            status_class = "status-high"
            status_text = "EXTREM HOCH"
        elif current_level < 10:
            status_class = "status-low"
            status_text = "EXTREM TIEF"
        
        html += f"""
        <div class="champion-card {status_class}">
            <strong>{ticker}</strong><br>
            <span class="count-badge">{count}x dabei</span><br>
            <small>{status_text}</small>
        </div>
        """
    
    html += "</div>"
    return html

# Ausführung
ranking = calculate_champion_ranking()
full_ui_component = generate_slider_html(ranking)
print("Komponente generiert.")
