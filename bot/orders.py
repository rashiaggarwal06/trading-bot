from decimal import Decimal
from typing import Optional

from bot.client import BinanceClient
from bot.logging_config import setup_logger
from bot.validators import validate_order_inputs

logger = setup_logger("orders")


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> dict:
    """Validate inputs and place an order via the Binance client."""

    # Validate
    symbol, side, order_type, qty_decimal, price_decimal = validate_order_inputs(
        symbol, side, order_type, quantity, price
    )

    stop_decimal = None
    if stop_price is not None:
        from bot.validators import validate_price
        stop_decimal = validate_price(stop_price)

    # Print summary before placing
    print("\n" + "=" * 50)
    print("  ORDER REQUEST SUMMARY")
    print("=" * 50)
    print(f"  Symbol     : {symbol}")
    print(f"  Side       : {side}")
    print(f"  Type       : {order_type}")
    print(f"  Quantity   : {qty_decimal}")
    if price_decimal:
        print(f"  Price      : {price_decimal}")
    if stop_decimal:
        print(f"  Stop Price : {stop_decimal}")
    print("=" * 50)

    logger.info(
        "Order request | symbol=%s side=%s type=%s qty=%s price=%s",
        symbol, side, order_type, qty_decimal, price_decimal,
    )

    # Place
    response = client.place_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=qty_decimal,
        price=price_decimal,
        stop_price=stop_decimal,
    )

    logger.info("Order response: %s", response)

    # Print response
    print("\n  ORDER RESPONSE")
    print("=" * 50)
    print(f"  Order ID     : {response.get('orderId', 'N/A')}")
    print(f"  Status       : {response.get('status', 'N/A')}")
    print(f"  Executed Qty : {response.get('executedQty', '0')}")
    avg_price = response.get('avgPrice') or response.get('price', 'N/A')
    print(f"  Avg Price    : {avg_price}")
    print(f"  Client OID   : {response.get('clientOrderId', 'N/A')}")
    print("=" * 50)
    print("  ✅ Order placed successfully!")
    print("=" * 50 + "\n")

    return response
