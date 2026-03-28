import yfinance as yf

def analyze_watchlist(watchlist, risk_per_trade_eur=500):
    """
    Analysiert eine Liste von Aktien basierend auf dem 3-10 Tage Programm.
    """
    print(f"{'SYMBOL':<10} | {'PREIS':<10} | {'STÜCK':<7} | {'VOLUMEN':<12} | {'CRV':<5} | {'STATUS'}")
    print("-" * 75)

    for symbol, params in watchlist.items():
        try:
            # Daten abrufen
            ticker = yf.Ticker(symbol)
            # Aktueller Kurs
            current_price = ticker.fast_info['last_price']
            
            stop_loss = params['sl']
            take_profit = params['tp']
            
            # Risikokalkulation
            risk_per_share = abs(current_price - stop_loss)
            
            if risk_per_share <= 0:
                print(f"{symbol:<10} | Fehler: Stop-Loss zu nah am Preis.")
                continue

            # Stückzahl berechnen (Risiko / Differenz)
            shares = int(risk_per_trade_eur / risk_per_share)
            total_position_value = shares * current_price
            
            # CRV und Ziel-Check (3-5-7 Regel)
            potential_gain = abs(take_profit - current_price)
            crv = potential_gain / risk_per_share
            profit_pct = (potential_gain / current_price) * 100
            
            # Status-Check
            status = "OK"
            if profit_pct < 7:
                status = "(!) Ziel < 7%"
            if crv < 1.5:
                status = "(!) CRV schwach"

            # Ergebnis ausgeben
            print(f"{symbol:<10} | {current_price:>10.2f} | {shares:>7} | {total_position_value:>10.2f} | {crv:>5.2f} | {status}")

        except Exception as e:
            print(f"{symbol:<10} | Fehler beim Abrufen: {e}")

# --- KONFIGURATION DEINER TRADING-CHANCEN ---
# Trage hier deine Werte ein: sl = Stop-Loss, tp = Take-Profit
my_watchlist = {
    "NVDA":    {"sl": 122.50, "tp": 145.00},  # Nvidia (US)
    "SAP.DE":  {"sl": 175.00, "tp": 195.00},  # SAP (DE)
    "RHM.DE":  {"sl": 495.00, "tp": 560.00},  # Rheinmetall (DE)
    "AAPL":    {"sl": 185.00, "tp": 215.00}   # Apple (US)
}

# Programm starten
if __name__ == "__main__":
    print("Starte Programm: Tradingchancen (Haltedauer 3-10 Tage)")
    print(f"Fixes Risiko pro Trade: 500 EUR\n")
    analyze_watchlist(my_watchlist)
