# Trading Bot — Binance Futures Testnet

A lightweight Python CLI application for placing orders on Binance Futures Testnet (USDT-M).

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance API client (signing, HTTP)
│   ├── orders.py          # Order placement logic + output formatting
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Structured file + console logging
├── cli.py                 # CLI entry point (argparse)
├── logs/                  # Auto-created; log files stored here
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd trading_bot
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Binance Futures Testnet credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Sign in with GitHub
3. Navigate to **API Key** section → Generate a key pair
4. Copy your API Key and Secret

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

---

## How to Run

### Place a Market Order

```bash
# BUY 0.001 BTC at market price
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# SELL 0.001 BTC at market price
python cli.py order --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### Place a Limit Order

```bash
# BUY 0.001 BTC at $60,000
python cli.py order --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 60000

# SELL 0.001 BTC at $70,000
python cli.py order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

### Place a Stop-Market Order (Bonus)

```bash
# Trigger a BUY if price rises above $66,000
python cli.py order --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 66000
```

### View Account Balance

```bash
python cli.py account
```

---

## Sample Output

```
==================================================
  ORDER REQUEST SUMMARY
==================================================
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
==================================================

  ORDER RESPONSE
==================================================
  Order ID     : 3942581234
  Status       : FILLED
  Executed Qty : 0.001
  Avg Price    : 67432.10
  Client OID   : abc123xyz
==================================================
  ✅ Order placed successfully!
==================================================
```

---

## Logging

All API requests, responses, and errors are logged to `logs/trading_YYYYMMDD.log`.

Log format:
```
2026-06-01 14:23:01 | DEBUG    | client | POST https://testnet.binancefuture.com/fapi/v1/order | params: {...}
2026-06-01 14:23:02 | INFO     | orders | Order response: {'orderId': 394258, 'status': 'FILLED', ...}
```

---

## Assumptions

- All orders are placed on **Binance Futures Testnet (USDT-M)** only — not mainnet.
- `timeInForce` for LIMIT orders is set to `GTC` (Good Till Cancelled) by default.
- Quantity precision must match Binance's symbol rules (e.g., BTCUSDT min qty = 0.001).
- API credentials are loaded from a `.env` file using `python-dotenv`.

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing API keys | Prints clear message, exits with code 1 |
| Invalid input (side/type/qty) | Prints validation error, exits with code 1 |
| API error (e.g. insufficient balance) | Prints API error code + message |
| Network failure | Prints connection error message |
| Timeout | Prints timeout message |
