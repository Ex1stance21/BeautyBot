import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.queries import get_bookings_for_reminder, mark_reminder_sent
from config import REMINDER_HOURS_BEFORE

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def check_reminders(bot):
    """Перевіряє записи та надсилає нагадування."""
    now = datetime.now()
    bookings = await get_bookings_for_reminder()

    for b in bookings:
        try:
            booking_dt = datetime.strptime(
                f"{b['booking_date']} {b['booking_time']}",
                "%Y-%m-%d %H:%M"
            )
            time_until = booking_dt - now

            if timedelta(0) < time_until <= timedelta(hours=REMINDER_HOURS_BEFORE):
                hours = int(time_until.total_seconds() // 3600)
                minutes = int((time_until.total_seconds() % 3600) // 60)
                time_text = f"{hours} год {minutes} хв" if hours > 0 else f"{minutes} хв"

                await bot.send_message(
                    b["user_id"],
                    f"⏰ <b>Нагадування!</b>\n\n"
                    f"Ваш запис на <b>{b['service_name']}</b> "
                    f"через <b>{time_text}</b>!\n\n"
                    f"📅 {b['booking_date']} о {b['booking_time']}\n\n"
                    f"Чекаємо на вас! 💅"
                )
                await mark_reminder_sent(b["id"])
                logger.info(f"Reminder sent for booking #{b['id']}")

        except Exception as e:
            logger.error(f"Failed to send reminder for booking #{b['id']}: {e}")


async def start_reminder_scheduler(bot):
    """Запускає планувальник нагадувань (кожні 15 хв)."""
    scheduler.add_job(
        check_reminders,
        "interval",
        minutes=15,
        args=[bot],
        id="reminder_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info("✅ Reminder scheduler started (every 15 min)")
