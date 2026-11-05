
import numpy as np
import pandas as pd

def add_indicators(df):
    x = df.copy()
    close = x["Close"]

    x["EMA_20"] = close.ewm(span=20, adjust=False).mean()
    x["EMA_50"] = close.ewm(span=50, adjust=False).mean()

    delta = close.diff()
    gain = delta.clip(lower=0).ewm(
        alpha=1/14, adjust=False
    ).mean()
    loss = (-delta.clip(upper=0)).ewm(
        alpha=1/14, adjust=False
    ).mean()

    rs = gain / loss.replace(0, np.nan)
    x["RSI_14"] = 100 - (100 / (1 + rs))

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()

    x["MACD"] = ema12 - ema26
    x["MACD_SIGNAL"] = x["MACD"].ewm(
        span=9, adjust=False
    ).mean()

    return x.dropna()


def generate_signal(df):
    if len(df) < 3:
        return {
            "action": "WAIT",
            "reason": "Not enough data"
        }

    last = df.iloc[-1]

    if (
        last["EMA_20"] > last["EMA_50"]
        and last["RSI_14"] > 50
        and last["MACD"] > last["MACD_SIGNAL"]
    ):
        return {
            "action": "BUY",
            "reason": "Bullish trend confirmed by indicators"
        }

    if (
        last["EMA_20"] < last["EMA_50"]
        and last["RSI_14"] < 50
        and last["MACD"] < last["MACD_SIGNAL"]
    ):
        return {
            "action": "SELL",
            "reason": "Bearish trend confirmed by indicators"
        }

    return {
        "action": "WAIT",
        "reason": "Indicators are mixed"
    }


def backtest(df, fee_bps=5, slippage_bps=5):
    x = df.copy()

    long_cond = (
        (x["EMA_20"] > x["EMA_50"])
        & (x["RSI_14"] > 50)
        & (x["MACD"] > x["MACD_SIGNAL"])
    )

    short_cond = (
        (x["EMA_20"] < x["EMA_50"])
        & (x["RSI_14"] < 50)
        & (x["MACD"] < x["MACD_SIGNAL"])
    )

    x["position"] = np.select(
        [long_cond, short_cond],
        [1, -1],
        default=0
    )

    x["position"] = x["position"].shift(1).fillna(0)
    x["asset_return"] = x["Close"].pct_change().fillna(0)

    turnover = (
        x["position"].diff().abs()
        .fillna(x["position"].abs())
    )

    cost = (fee_bps + slippage_bps) / 10000

    x["strategy_return"] = (
        x["position"] * x["asset_return"]
        - turnover * cost
    )

    equity = (1 + x["strategy_return"]).cumprod()
    peak = equity.cummax()
    drawdown = equity / peak - 1

    trade_changes = (
        x["position"].diff()
        .fillna(x["position"]).ne(0)
    )

    trade_returns = x.loc[
        trade_changes, "strategy_return"
    ]

    trade_returns = trade_returns[trade_returns != 0]

    wins = int((trade_returns > 0).sum())
    n = len(trade_returns)

    return {
        "return_pct": float((equity.iloc[-1] - 1) * 100),
        "max_drawdown_pct": float(drawdown.min() * 100),
        "trades": n,
        "win_rate": float(wins / n * 100) if n else 0.0
                   }
      
