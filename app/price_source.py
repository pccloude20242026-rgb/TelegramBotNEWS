from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import settings

TWELVEDATA_URL = "https://api.twelvedata.com/price"
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"


@dataclass
class PriceQuote:
    symbol: str
    label: str
    price: float | None
    error: str | None = None


# Twelve Data orqali olinadigan simvollar
# Eslatma: WTI/USD (neft) Twelve Data'ning bepul planida mavjud
# bo'lmasligi mumkin — shunday holatda pullik planga o'tish kerak
# yoki alohida neft manbasi (masalan, EIA API) ulanadi.
TWELVEDATA_SYMBOLS = {
    "XAU/USD": "Oltin (XAU/USD)",
    "XAG/USD": "Kumush (XAG/USD)",
    "WTI/USD": "Neft — WTI (WTI/USD)",
    "USD/UZS": "Dollar / So'm (USD/UZS)",
}


async def _fetch_twelvedata_price(client: httpx.AsyncClient, symbol: str) -> PriceQuote:
    label = TWELVEDATA_SYMBOLS[symbol]
    try:
        resp = await client.get(
            TWELVEDATA_URL,
            params={"symbol": symbol, "apikey": settings.twelvedata_api_key},
        )
        data = resp.json()
        if "price" in data:
            return PriceQuote(symbol=symbol, label=label, price=float(data["price"]))
        return PriceQuote(symbol=symbol, label=label, price=None, error=data.get("message", "xato"))
    except Exception as exc:  # noqa: BLE001
        return PriceQuote(symbol=symbol, label=label, price=None, error=str(exc))


async def _fetch_btc_price(client: httpx.AsyncClient) -> PriceQuote:
    try:
        resp = await client.get(BINANCE_URL, params={"symbol": "BTCUSDT"})
        data = resp.json()
        return PriceQuote(symbol="BTC/USD", label="Bitcoin (BTC/USD)", price=float(data["price"]))
    except Exception as exc:  # noqa: BLE001
        return PriceQuote(symbol="BTC/USD", label="Bitcoin (BTC/USD)", price=None, error=str(exc))


async def fetch_all_prices() -> list[PriceQuote]:
    async with httpx.AsyncClient(timeout=15) as client:
        results = []
        for symbol in TWELVEDATA_SYMBOLS:
            results.append(await _fetch_twelvedata_price(client, symbol))
        results.append(await _fetch_btc_price(client))
        return results
