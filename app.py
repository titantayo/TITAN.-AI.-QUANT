import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from engine.market_data import fetch_market_data
from engine.strategy import add_indicators, generate_signal, backtest

st.set_page_config(page_title="TITAN AI QUANT", page_icon="📈", layout="wide")
st.markdown("""
<style>
.stApp {background:#080d18;color:#edf2f7}
[data-testid="stMetric"] {background:#111a2b;padding:14px;border:1px solid #26334b;border-radius:12px}
h1,h2,h3 {color:#e5bd68}
</style>
""", unsafe_allow_html=True)

st.title("◈ TITAN AI QUANT")
st.caption("Quantitative market research • Signals • Backtesting • Paper trading")
st.warning("RESEARCH / PAPER MODE ONLY — no real orders are placed by this application.")

with st.sidebar:
    st.header("Market settings")
    market = st.selectbox("Market", ["Crypto", "Forex"])
    choices = {
        "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
        "Forex": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "GC=F"]
    }
    symbol = st.selectbox("Instrument", choices[market])
    interval = st.selectbox("Timeframe", ["15m", "1h", "1d"], index=1)
    period = st.selectbox("History", ["7d", "30d", "90d", "1y"], index=2)
    refresh = st.button("Fetch / refresh market data", use_container_width=True)

@st.cache_data(ttl=90)
def load_data(ticker, timeframe, history):
    return fetch_market_data(ticker, timeframe, history)

try:
    raw = load_data(symbol, interval, period)
    if raw is None or raw.empty:
        st.error("No market data was returned. Try another instrument or timeframe.")
        st.stop()
    data = add_indicators(raw)
    signal = generate_signal(data)
    stats = backtest(data)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Instrument", symbol)
    c2.metric("Latest close", f"{data.Close.iloc[-1]:,.5f}")
    c3.metric("Quant signal", signal["action"])
    c4.metric("Backtest return", f'{stats["return_pct"]:.2f}%')

    st.subheader("Market structure")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data.Open, high=data.High,
                                 low=data.Low, close=data.Close, name="Price"))
    fig.add_trace(go.Scatter(x=data.index, y=data.EMA_20, name="EMA 20"))
    fig.add_trace(go.Scatter(x=data.index, y=data.EMA_50, name="EMA 50"))
    fig.update_layout(template="plotly_dark", height=520, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    left,right = st.columns(2)
    with left:
        st.subheader("Signal analysis")
        st.write(f'**Action:** {signal["action"]}')
        st.write(f'**Reason:** {signal["reason"]}')
        st.write(f'**RSI (14):** {data.RSI_14.iloc[-1]:.2f}')
        st.write(f'**MACD:** {data.MACD.iloc[-1]:.5f}')
        st.caption("This is a rule-based research signal, not a prediction or guaranteed trade.")
    with right:
        st.subheader("Historical backtest")
        st.metric("Closed trades", stats["trades"])
        st.metric("Win rate", f'{stats["win_rate"]:.1f}%')
        st.metric("Max drawdown", f'{stats["max_drawdown_pct"]:.2f}%')
        st.caption("Illustrative historical simulation. Results do not predict future performance.")

    st.subheader("Latest market data")
    st.dataframe(data.tail(15).sort_index(ascending=False), use_container_width=True)
    st.download_button("Download market data CSV", data.to_csv().encode(), f"{symbol}_{interval}.csv", "text/csv")
except Exception as exc:
    st.error(f"Market data could not be loaded: {exc}")
    st.info("This starter uses Yahoo Finance through yfinance. Data coverage, delays and interval availability vary.")
