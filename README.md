# TITAN AI QUANT — free-first starter

A research dashboard for Forex and crypto market data, transparent indicator signals, and an educational historical backtest.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy free
1. Create a GitHub repository and upload this project.
2. Sign in at https://share.streamlit.io/
3. Select the repository, branch, and `app.py`.
4. Deploy.

## Important limitations
- This version does not place orders and is not connected to a broker.
- Yahoo Finance/yfinance is a convenience research feed, not an institutional or guaranteed real-time feed. Coverage and intervals vary.
- Backtest results are simplified and are not proof of future profitability. Validate with out-of-sample data, realistic fees, spreads, slippage, funding and execution assumptions before relying on results.
- Do not put API keys in source code. Use platform secrets for any future credentials.
- Real trading must remain disabled until a separate execution service, broker/exchange testnet, monitoring, and hard risk limits are implemented.
