from decimal import Decimal, InvalidOperation


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s or len(s) < 5:
        raise ValueError(f"Invalid symbol '{symbol}'. Example: BTCUSDT")
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}")
    return s


def validate_order_type(order_type: str) -> str:
    o = order_type.strip().upper()
    if o not in VALID_ORDER_TYPES:
        raise ValueError(f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}")
    return o


def validate_quantity(quantity: str) -> Decimal:
    try:
        qty = Decimal(str(quantity))
        if qty <= 0:
            raise ValueError
        return qty
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")


def validate_price(price: str) -> Decimal:
    try:
        p = Decimal(str(price))
        if p <= 0:
            raise ValueError
        return p
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid price '{price}'. Must be a positive number.")


def validate_order_inputs(symbol, side, order_type, quantity, price=None):
    """Validate all order inputs together and return cleaned values."""
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)

    if order_type in ("LIMIT", "STOP_MARKET") and price is None:
        raise ValueError(f"Price is required for {order_type} orders.")

    if price is not None:
        price = validate_price(price)

    return symbol, side, order_type, quantity, price
