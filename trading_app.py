import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- NEU: ANALYSE NACH MARKET MAKER LOGIK ---
def analyze_market_maker_flow(ticker, df):
    cp = float(df['Close'].iloc[-1])
    
    # 1. Volatilität für MM-Spreads (ATR)
    df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    atr = float(df['TR'].tail(14).mean())
    
    # 2. Volumen-Validierung (Wo sitzt das institutionelle Geld?)
    df['Vol_SMA20'] = df['Volume'].rolling(window=20).mean()
    high_volume_break = df['Volume'].iloc[-1] > (df['Vol_SMA20'].iloc[-1] * 1.5)
    
    # 3. Liquiditäts-Zonen (Support/Resistance basierend auf Swing Highs/Lows der letzten 20 Tage)
    liquidity_pool_high = float(df['High'].tail(20).max())
    liquidity_pool_low = float(df['Low'].tail(20).min())
    
    # 4. Market Maker Logik: "Stop Hunting" & "Liquidity Grab"
    # Wenn der Kurs nah an die Extrempunkte (Pools) herankommt, greift der MM die Liquidität ab
    dist_to_low = (cp - liquidity_pool_low) / cp
    dist_to_high = (liquidity_pool_high - cp) / cp
    
    # Berechnung des 3-Tage-Trends für die Richtung des Impulses
    prev_3d = float(df['Close'].iloc[-4])
    chg_3d = ((cp / prev_3d) - 1) * 100
    
    # SIGNAL-GENERIERUNG
    # CALL: Kurs hat den unteren Liquiditätspool fast erreicht/durchbrochen und Volumen steigt (Institutionelle Absorption)
    if dist_to_low < 0.02 and high_volume_break:
        direction = 1  # INSTITUTIONAL BUY / CALL
        chance = 75.0 + (abs(chg_3d) * 0.1)
        signal_type = "Liquidity Grab (Buy)"
    # PUT: Kurs kratzt am oberen Liquiditätspool, Institutionelle laden Positionen ab
    elif dist_to_high < 0.02 and high_volume_break:
        direction = -1 # INSTITUTIONAL SUPPLY / PUT
        chance = 70.0 + (abs(chg_3d) * 0.1)
        signal_type = "Liquidity Grab (Sell)"
    else:
        # Standard Orderflow-Trendfolge, wenn keine extremen Zonen erreicht sind
        direction = 1 if chg_3d > 0 else -1
        chance = 50.0 + (abs(chg_3d) * 0.2)
        signal_type = "Standard Order Flow"

    # Wetter-Icon Logik adaptieren
    weather = "☀️" if direction == 1 else "⛈️"
    dot = "🟢" if direction == 1 else "🔴"
    
    return {
        "cp": cp, "chg_3d": chg_3d, "atr": atr, "weather": weather, 
        "dot": dot, "chance": chance, "direction": direction, "df": df,
        "pool_high": liquidity_pool_high, "pool_low": liquidity_pool_low, "type": signal_type
    }
