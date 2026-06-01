import hashlib
import hmac
import time
from decimal import Decimal
from typing import Optional
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"
logger = setup_logger("client")


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _post(self, endpoint: str, params: dict) -> dict:
        url = f"{BASE_URL}{endpoint}"
        signed_params = self._sign(params)

        logger.debug("POST %s | params: %s", url, {k: v for k, v in signed_params.items() if k != "signature"})

        try:
            response = self.session.post(url, params=signed_params, timeout=10)
            data = response.json()
            logger.debug("Response [%s]: %s", response.status_code, data)

            if response.status_code != 200:
                error_msg = data.get("msg", "Unknown API error")
                error_code = data.get("code", response.status_code)
                logger.error("API error %s: %s", error_code, error_msg)
                raise RuntimeError(f"API Error {error_code}: {error_msg}")

            return data

        except requests.exceptions.ConnectionError:
            logger.error("Network error: could not connect to %s", BASE_URL)
            raise ConnectionError("Network error: could not reach Binance Futures Testnet. Check your internet connection.")
        except requests.exceptions.Timeout:
            logger.error("Request timed out for %s", url)
            raise TimeoutError("Request timed out. Try again.")
        except requests.exceptions.RequestException as e:
            logger.error("Unexpected request error: %s", e)
            raise RuntimeError(f"Request failed: {e}")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
    ) -> dict:
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": str(quantity),
        }

        if order_type == "LIMIT":
            params["price"] = str(price)
            params["timeInForce"] = "GTC"

        if order_type == "STOP_MARKET" and stop_price:
            params["stopPrice"] = str(stop_price)

        logger.info(
            "Placing %s %s order | symbol=%s qty=%s price=%s",
            side, order_type, symbol, quantity, price or "MARKET",
        )

        return self._post("/fapi/v1/order", params)

    def get_account_info(self) -> dict:
        params = {}
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature

        url = f"{BASE_URL}/fapi/v2/account"
        logger.debug("GET %s", url)
        response = self.session.get(url, params=params, timeout=10)
        return response.json()
