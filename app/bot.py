from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

from aiogram import Bot
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.formatter import format_news, format_prices
from app.news_source import fetch_events, filter_by_min_impact, only_released_recent
from app.price_source import fetch_fast_prices, fetch_slow_prices

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("forex_news_bot")

STATE_FILE = Path("state.json")


def _load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"posted_news_ids": [], "last_prices": {}}


def _save_state(state: dict) -> None:
    # oxirgi 500 ta ID'ni saqlaymiz, fayl cheksiz o'smasligi uchun
    state["posted_news_ids"] = state["posted_news_ids"][-500:]
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False))


async def news_job(bot: Bot, state: dict) -> None:
    try:
        events = await fetch_events()
    except Exception as exc:  # noqa: BLE001
        log.warning("Yangiliklarni olishda xato: %s", exc)
        return

    events = filter_by_min_impact(events, settings.min_news_impact)
    events = only_released_recent(events, within_minutes=settings.news_check_interval // 60 + 5)

    new_events = [e for e in events if e.id not in state["posted_news_ids"]]
    for event in new_events:
        text = format_news(event)
        try:
            await bot.send_message(settings.channel_id, text, parse_mode=ParseMode.HTML)
            state["posted_news_ids"].append(event.id)
            log.info("Yangilik yuborildi: %s", event.title)
        except Exception as exc:  # noqa: BLE001
            log.warning("Xabar yuborishda xato: %s", exc)

    if new_events:
        _save_state(state)


async def fast_price_job(bot: Bot, state: dict) -> None:
    """Oltin, Kumush, BTC — cheklovsiz manba, tez-tez yuboriladi."""
    quotes = await fetch_fast_prices()
    text = format_prices(
        quotes,
        previous=state.get("last_prices", {}),
        title="💹 <b>Bozor narxlari</b>",
    )

    try:
        await bot.send_message(settings.channel_id, text, parse_mode=ParseMode.HTML)
    except Exception as exc:  # noqa: BLE001
        log.warning("Narx xabarini yuborishda xato: %s", exc)
        return

    state.setdefault("last_prices", {})
    state["last_prices"].update({q.symbol: q.price for q in quotes if q.price is not None})
    _save_state(state)


async def slow_price_job(bot: Bot, state: dict) -> None:
    """Neft (WTI) va USD/UZS — cheklangan/kunlik manba, kamroq yuboriladi."""
    quotes = await fetch_slow_prices()
    text = format_prices(
        quotes,
        previous=state.get("last_prices", {}),
        title="🛢 <b>Neft va valyuta kursi</b>",
    )

    try:
        await bot.send_message(settings.channel_id, text, parse_mode=ParseMode.HTML)
    except Exception as exc:  # noqa: BLE001
        log.warning("Neft/valyuta xabarini yuborishda xato: %s", exc)
        return

    state.setdefault("last_prices", {})
    state["last_prices"].update({q.symbol: q.price for q in quotes if q.price is not None})
    _save_state(state)


async def main() -> None:
    bot = Bot(token=settings.bot_token)
    state = _load_state()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(news_job, "interval", seconds=settings.news_check_interval, args=[bot, state])
    scheduler.add_job(
        fast_price_job, "interval", seconds=settings.fast_price_update_interval, args=[bot, state]
    )
    scheduler.add_job(
        slow_price_job, "interval", seconds=settings.slow_price_update_interval, args=[bot, state]
    )
    scheduler.start()

    log.info("Bot ishga tushdi. Kanal: %s", settings.channel_id)

    # Ishga tushishi bilan darhol bir marta ishlatib ko'ramiz
    await fast_price_job(bot, state)
    await slow_price_job(bot, state)
    await news_job(bot, state)

    # Doim ishlab tursin
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
