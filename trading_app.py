import yfinance as yf
import pandas as pd
import sys

# --- 1. KONFIGURATION (Hier deine Daten anpassen) ---
RISIKO_PRO_TRADE = 500  # Dein festes Risiko in EUR
WATCHLIST = {
    "NVDA":    {"sl": 120.00, "tp": 150.00}, # Nvidia
    "SAP.DE":  {"sl": 170.00, "tp": 200.00}, # SAP (Xetra)
    "RHM.DE":  {"sl": 480.00, "tp": 550.00}, # Rheinmetall (Xetra)
    "AAPL":    {"sl": 185.00, "tp": 215.00}  # Apple
}

def check_trading_chancen():
    print("="*60)
    print("PROGRAMM GESTARTET: Tradingchancen (3-10 Tage)")
    print(f"Risiko pro Trade: {RISIKO_PRO_TRADE} EUR")
    print("="*60)
    
    ergebnisse_gefunden = False

    for symbol, params in WATCHLIST.items():
        try:
            print(f"Lade Daten für {symbol}...", end="\r")
            ticker = yf.Ticker(symbol)
            # Nutze 5 Tage Historie, um sicherzugehen (Wochenende/Feiertage)
            data = ticker.history(period="5d")
            
            if data.empty:
                print(f"[-] {symbol}: Keine Daten von Yahoo erhalten.")
                continue
            
            aktuelle_kurs = data['Close'].iloc[-1]
            sl = params['sl']
            tp = params['tp']
            
            # Berechnung Risiko pro Aktie
            risiko_pro_aktie = abs(aktuelle_kurs - sl)
            
            if risiko_pro_aktie < 0.01:
                print(f"[-] {symbol}: Stop-Loss zu nah am Kurs ({aktuelle_kurs:.2f}).")
                continue

            # Stückzahl berechnen (Risiko / Differenz)
            stueckzahl = int(RISIKO_PRO_TRADE / risiko_pro_aktie)
            positions_wert = stueckzahl * aktuelle_kurs
            
            # Kennzahlen (3-5-7 Regel Check)
            gewinn_potential = abs(tp - aktuelle_kurs)
            crv = gewinn_potential / risiko_pro_aktie
            rendite_ziel = (gewinn_potential / aktuelle_kurs) * 100
            
            # Ausgabe der Zeile
            status = "PASSEND" if rendite_ziel >= 7 else "ZIEL < 7%"
            
            print(f"SYMBOL: {symbol:<8} | KURS: {aktuelle_kurs:>8.2f} | STÜCK: {stueckzahl:>4} | WERT: {positions_wert:>10.2f} | CRV: {crv:>4.2f} | {status}")
            ergebnisse_gefunden = True

        except Exception as e:
            print(f"[-] Fehler bei {symbol}: {e}")

    if not ergebnisse_gefunden:
        print("\nKeine gültigen Setups gefunden. Prüfe Internetverbindung oder Ticker-Symbole.")
    
    print("="*60)
    print("SCAN BEENDET.")

# --- 2. STARTBEFEHL (Wichtig: Ohne das läuft nichts!) ---
if __name__ == "__main__":
    try:
        check_trading_chancen()
    except KeyboardInterrupt:
        print("\nAbgebrochen durch Nutzer.")
    except Exception as e:
        print(f"Kritischer Programmfehler: {e}")
