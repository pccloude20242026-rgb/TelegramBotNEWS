from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import settings

GOLD_API_BASE = "https://api.gold-api.com"
OILPRICE_API_URL = "https://api.oilpriceapi.com/v1/prices/latest"
CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/all/"
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"


@dataclass
class PriceQuote:
    symbol: str
    label: str
    price: float | None
    error: str | None = None


# ---------------------------------------------------------------------------
# Tez yangilanadigan narxlar: Oltin, Kumush, BTC
# gold-api.com — API key shart emas, so'rov soniga cheklov yo'q (real vaqt).
# Manba: https://gold-api.com/llms.txt
# ---------------------------------------------------------------------------
GOLD_API_SYMBOLS = {
    "XAU": "Oltin (XAU/USD)",
    "XAG": "Kumush (XAG/USD)",
}


async def _fetch_gold_api_price(client: httpx.AsyncClient, symbol: str) -> PriceQuote:
    label = GOLD_API_SYMBOLS[symbol]
    try:
        resp = await client.get(f"{GOLD_API_BASE}/price/{symbol}")
        data = resp.json()
        return PriceQuote(symbol=symbol, label=label, price=float(data["price"]))
    except Exception as exc:  # noqa: BLE001
        return PriceQuote(symbol=symbol, label=label, price=None, error=str(exc))


async def _fetch_btc_price(client: httpx.AsyncClient) -> PriceQuote:
    # Binance ham kalitsiz va bepul — BTC uchun eng barqaror manba
    try:
        resp = await client.get(BINANCE_URL, params={"symbol": "BTCUSDT"})
        data = resp.json()
        return PriceQuote(symbol="BTC/USD", label="Bitcoin (BTC/USD)", price=float(data["price"]))
    except Exception as exc:  # noqa: BLE001
        return PriceQuote(symbol="BTC/USD", label="Bitcoin (BTC/USD)", price=None, error=str(exc))


async def fetch_fast_prices() -> list[PriceQuote]:
    """Oltin, Kumush, BTC — har 1-5 daqiqada chaqirish uchun xavfsiz (limitsiz)."""
    async with httpx.AsyncClient(timeout=15) as client:
        results = [await _fetch_gold_api_price(client, s) for s in GOLD_API_SYMBOLS]
        results.append(await _fetch_btc_price(client))
        return results


# ---------------------------------------------------------------------------
# Sekin yangilanadigan narxlar: Neft (soatlik), USD/UZS (kunlik)
# Bepul reja cheklangan bo'lgani uchun bularni kamroq (masalan kuniga bir
# necha marta) chaqirish kerak — app/bot.py'da alohida, uzunroq interval
# bilan ishlaydi.
# ---------------------------------------------------------------------------
async def fetch_oil_price() -> PriceQuote:
    label = "Neft — WTI (WTI/USD)"
    if not settings.oilpriceapi_key:
        return PriceQuote(symbol="WTI", label=label, price=None, error="API key kiritilmagan")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                OILPRICE_API_URL,
                params={"by_code": "WTI_USD"},
                headers={"Authorization": f"Token {settings.oilpriceapi_key}"},
            )
            data = resp.json()
            price = data["data"]["price"]
            return PriceQuote(symbol="WTI", label=label, price=float(price))
    except Exception as exc:  # noqa: BLE001
        return PriceQuote(symbol="WTI", label=label, price=None, error=str(exc))


async def fetch_usd_uzs_price() -> PriceQuote:
    """O'zbekiston Markaziy banki rasmiy USD/UZS kursi (kalitsiz, bepul).
    Eslatma: bu rasmiy kurs kuniga bir marta yangilanadi, shuning uchun
    uni har daqiqada so'rashning ma'nosi yo'q."""
    label = "Dollar / So'm (USD/UZS, rasmiy CBU kursi)"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(CBU_URL)
            data = resp.json()
            usd_entry = next((item for item in data if item.get("Ccy") == "USD"), None)
            if not usd_entry:
                return PriceQuote(symbol="USD/UZS", label=label, price=None, error="USD topilmadi")
            rate = float(usd_entry["Rate"].replace(",", "."))
            return PriceQuote(symbol="USD/UZS", label=label, price=rate)
    except Exception as exc:  # noqa: BLE001
        return PriceQuote(symbol="USD/UZS", label=label, price=None, error=str(exc))


async def fetch_slow_prices() -> list[PriceQuote]:
    return [await fetch_oil_price(), await fetch_usd_uzs_price()]


async def fetch_all_prices() -> list[PriceQuote]:
    """Barcha narxlarni birga olish (masalan, /narxlar buyrug'i uchun)."""
    fast = await fetch_fast_prices()
    slow = await fetch_slow_prices()
    return fast + slow
