import pandas as pd

def check_trading_setup(symbol, price, stop_loss, take_profit, risk_per_trade_eur=500, vix_level=20, adx_level=25):
    """
    Berechnet Trading-Parameter basierend auf unserem 3-10 Tage Programm.
    """
    
    # 1. VIX-Filter (Volatilitäts-Check)
    if vix_level > 25:
        return f"STOPP: VIX bei {vix_level}. Volatilität zu hoch für 3-10 Tage Swings. Keine Trades!"

    # 2. Trendstärke-Check (ADX)
    if adx_level < 20:
        return f"STOPP: ADX bei {adx_level}. Kein klarer Trend sichtbar. Seitwärtsphase vermeiden."

    # 3. Risikomanagement (Positionsgröße)
    risk_per_share = abs(price - stop_loss)
    
    if risk_per_share == 0:
        return "Fehler: Stop-Loss darf nicht gleich dem Einstiegspreis sein."

    # Berechnung Stückzahl (Einheit pro Trading 500€ Risiko)
    shares_to_buy = int(risk_per_trade_eur / risk_per_share)
    
    # 4. Chance-Risiko-Verhältnis (CRV) - Ziel: Mindestens 7% Gewinn (3-5-7 Regel)
    potential_profit_per_share = abs(take_profit - price)
    crv = potential_profit_per_share / risk_per_share
    profit_percent = (potential_profit_per_share / price) * 100

    # Output
    print(f"--- Setup für {symbol} ---")
    print(f"Einstieg: {price} | Stop-Loss: {stop_loss} | Ziel: {take_profit}")
    print(f"Stückzahl für 500€ Risiko: {shares_to_buy} Einheiten")
    print(f"Positionsgröße gesamt: {shares_to_buy * price:.2f} EUR/USD")
    print(f"Erwarteter Gewinn: {shares_to_buy * potential_profit_per_share:.2f} EUR/USD")
    print(f"CRV: {crv:.2f} | Ziel-Rendite: {profit_percent:.2f}%")
    
    if profit_percent < 7:
        print("WARNUNG: Zielrendite unter 7% (Verletzung der 3-5-7 Regel)")

# BEISPIEL-DATEN (Ende März 2026)
# Nvidia Long-Versuch
check_trading_setup(
    symbol="NVDA", 
    price=181.50, 
    stop_loss=172.00, 
    take_profit=198.00, 
    vix_level=22,  # Markt ist noch okay
    adx_level=28   # Trend ist stark genug
)
