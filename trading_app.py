import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. LOGIK: Champions filtern ---
def get_dynamic_champions(pool_tickers, limit=7):
    all_data = []
    for t_sym in pool_tickers:
        try:
            ticker = yf.Ticker(t_sym)
            df = ticker.history(period="20d")
            if not df.empty and len(df) > 1:
                name = ticker.info.get('shortName', t_sym)
                preis = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                diff = ((preis - prev) / prev) * 100
                
                # RSI / Position [cite: 2026-02-07]
                low14, high14 = df['Close'].tail(14).min(), df['Close'].tail(14).max()
                pos_pct = ((preis - low14) / (high14 - low14)) * 100 if high14 != low14 else 50
                
                # ATR für die "Champions"-Sortierung (Hidden Champions = oft hohe Vola)
                atr = (df['High'] - df['Low']).tail(14).mean()
                
                all_data.append({
                    "Trend": f"{'☀️' if pos_pct > 90 else '🌧️' if pos_pct < 10 else '☁️'}{'🟢' if diff > 0.01 else '🔴' if diff < -0.01 else '🟡'}",
                    "Name": name,
                    "Symbol": t_sym,
                    "Preis(EUR)": f"{preis:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    "Pos%": f"{pos_pct:.1f}%",
                    "ATR": round(atr, 2),
                    "Status": "EXTREM HOCH" if pos_pct > 90 else "EXTREM TIEF" if pos_pct < 10 else "Normal"
                })
        except: continue
    
    # Erstellt DataFrame und gibt genau die Top 7 zurück
    df_final = pd.DataFrame(all_data)
    return df_final.head(limit) if not df_final.empty else df_final

# --- 2. ANZEIGE ---
st.markdown("### 🚀 KONTROLLTURM: DYNAMISCHE CHAMPIONS")

# Erweiteter Pool, aus dem das Skript die 7 Champions liest
pool_europa = ["OTP.BU", "MOL.BU", "ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE", "VOW3.DE", "BMW.DE"]
pool_usa = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD"]

st.write("**Europa: Top 7 Hidden Champions**")
st.dataframe(get_dynamic_champions(pool_europa), hide_index=True, use_container_width=True)

st.write("**USA: Top 7 Hidden Champions**")
st.dataframe(get_dynamic_champions(pool_usa), hide_index=True, use_container_width=True)

st.divider()
st.info("🧘 **Routine: WANDSITZ & RUHIG ATMEN!**")
