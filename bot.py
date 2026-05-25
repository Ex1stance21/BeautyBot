import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.db import init_db
from data.seed import seed_data
from handlers import start, services, booking, my_bookings, contacts, portfolio, reviews, admin
from utils.reminder import start_reminder_scheduler

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


async def main():
    # ── Bot & Dispatcher ──
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # ── Register routers ──
    dp.include_routers(
        start.router,
        services.router,
        booking.router,
        my_bookings.router,
        contacts.router,
        portfolio.router,
        reviews.router,
        admin.router,
    )

    # ── Init DB & seed ──
    await init_db()
    await seed_data()

    # ── Start reminder scheduler ──
    await start_reminder_scheduler(bot)

    # ── Start polling ──
    logger.info("🚀 Bot started! Press Ctrl+C to stop.")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
