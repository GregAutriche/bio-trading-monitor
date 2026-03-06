# --- BAUER SIGNAL-FUNKTION (3-Tage-Regel + SMA20) ---
def bauer_signal(df):
    # Schutz: Mindestens 25 Kerzen nötig (SMA20 + 3-Tage-Regel)
    if len(df) < 25:
        return None

    close = df["Close"]
    sma20 = close.rolling(20).mean()

    curr = close.iloc[-1]
    p1   = close.iloc[-2]
    p2   = close.iloc[-3]
    sma  = sma20.iloc[-1]

    if curr > p1 > p2 and curr > sma:
        return "C"
    if curr < p1 < p2 and curr < sma:
        return "P"
    return None


# --- BACKTESTING ENGINE ---
def backtest_strategy(df, signal_func, atr_mult_sl=1.5, atr_mult_tp=2.0, hold_days=5):
    df = df.copy()
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["ATR"] = (df["High"] - df["Low"]).rolling(14).mean()

    trades = []
    position = None

    for i in range(20, len(df) - hold_days):
        row = df.iloc[i]

        # WICHTIG: vollständigen DataFrame übergeben, nicht einzelne Zeile!
        sig = signal_func(df.iloc[:i+1])

        # Einstieg
        if position is None and sig in ["C", "P"]:
            entry = row["Close"]
            atr = row["ATR"]

            sl = entry - atr_mult_sl * atr if sig == "C" else entry + atr_mult_sl * atr
            tp = entry + atr_mult_tp * atr if sig == "C" else entry - atr_mult_tp * atr

            position = {
                "type": sig,
                "entry": entry,
                "sl": sl,
                "tp": tp,
                "entry_index": i
            }

        # Position überwachen
        if position:
            future = df.iloc[i:i+hold_days]
            exit_price = None
            exit_reason = None

            for _, f in future.iterrows():
                if position["type"] == "C":
                    if f["Low"] <= position["sl"]:
                        exit_price = position["sl"]
                        exit_reason = "SL"
                        break
                    if f["High"] >= position["tp"]:
                        exit_price = position["tp"]
                        exit_reason = "TP"
                        break
                else:
                    if f["High"] >= position["sl"]:
                        exit_price = position["sl"]
                        exit_reason = "SL"
                        break
                    if f["Low"] <= position["tp"]:
                        exit_price = position["tp"]
                        exit_reason = "TP"
                        break

            # Exit nach Zeitablauf
            if exit_price is None:
                exit_price = future.iloc[-1]["Close"]
                exit_reason = "TIME"

            pnl = exit_price - position["entry"] if position["type"] == "C" else position["entry"] - exit_price

            trades.append({
                "type": position["type"],
                "entry": position["entry"],
                "exit": exit_price,
                "pnl": pnl,
                "reason": exit_reason
            })

            position = None

    return pd.DataFrame(trades)


# --- PERFORMANCE ANALYSE ---
def evaluate_backtest(trades):
    if len(trades) == 0:
        return {}

    wins = trades[trades["pnl"] > 0]
    losses = trades[trades["pnl"] <= 0]

    return {
        "Trades": len(trades),
        "Trefferquote": len(wins) / len(trades) * 100,
        "Ø Gewinn": wins["pnl"].mean() if len(wins) else 0,
        "Ø Verlust": losses["pnl"].mean() if len(losses) else 0,
        "Profit Faktor": wins["pnl"].sum() / abs(losses["pnl"].sum()) if len(losses) else float("inf"),
        "Max Drawdown": (trades["pnl"].cumsum().cummax() - trades["pnl"].cumsum()).max(),
        "Gesamt PnL": trades["pnl"].sum()
    }


# --- STREAMLIT BACKTESTING-BEREICH ---
with st.expander("📈 Backtesting – Microsoft (MSFT)"):
    st.write("Backtest der Bauer-Strategie für Microsoft über 2 Jahre.")

    df_msft = yf.download("MSFT", period="2y", interval="1d", auto_adjust=True).dropna()

    trades = backtest_strategy(df_msft, bauer_signal)
    stats = evaluate_backtest(trades)

    if len(trades) == 0:
        st.warning("Keine Trades gefunden.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Trades", stats["Trades"])
        col2.metric("Trefferquote", f"{stats['Trefferquote']:.1f}%")
        col3.metric("Profit Faktor", f"{stats['Profit Faktor']:.2f}")

        col4, col5, col6 = st.columns(3)
        col4.metric("Ø Gewinn", f"{stats['Ø Gewinn']:.2f}")
        col5.metric("Ø Verlust", f"{stats['Ø Verlust']:.2f}")
        col6.metric("Max Drawdown", f"{stats['Max Drawdown']:.2f}")

        st.subheader("Equity-Kurve")
        st.line_chart(trades["pnl"].cumsum())

        st.subheader("Trades")
        st.dataframe(trades)
