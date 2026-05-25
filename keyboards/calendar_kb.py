import calendar
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.helpers import get_month_name_ua
from config import WORK_START_HOUR, WORK_END_HOUR, SLOT_DURATION_MINUTES


def get_calendar_kb(year: int = None, month: int = None) -> InlineKeyboardMarkup:
    """Інлайн-календар для вибору дати."""
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    buttons = []

    # ── Заголовок: < Травень 2026 > ──
    buttons.append([
        InlineKeyboardButton(text="◀️", callback_data=f"cal:prev:{year}:{month}"),
        InlineKeyboardButton(text=f"📅 {get_month_name_ua(month)} {year}", callback_data="cal:ignore"),
        InlineKeyboardButton(text="▶️", callback_data=f"cal:next:{year}:{month}"),
    ])

    # ── Дні тижня ──
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
    buttons.append([
        InlineKeyboardButton(text=d, callback_data="cal:ignore") for d in week_days
    ])

    # ── Дні місяця ──
    cal = calendar.monthcalendar(year, month)
    today = now.date()

    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="cal:ignore"))
            else:
                date = datetime(year, month, day).date()
                if date < today:
                    # Минулий день — неклікабельний
                    row.append(InlineKeyboardButton(text="·", callback_data="cal:ignore"))
                elif date.weekday() == 6:
                    # Неділя — вихідний
                    row.append(InlineKeyboardButton(text=f"✕", callback_data="cal:ignore"))
                else:
                    # Доступний день
                    label = f"✦{day}" if date == today else str(day)
                    row.append(InlineKeyboardButton(
                        text=label,
                        callback_data=f"cal:day:{year}:{month}:{day}"
                    ))
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def get_time_slots_kb(date_str: str, booked_times: list) -> InlineKeyboardMarkup:
    """Клавіатура вибору часу з урахуванням зайнятих слотів."""
    now = datetime.now()
    is_today = date_str == now.strftime("%Y-%m-%d")

    buttons = []
    row = []
    slot_count = 0

    hour = WORK_START_HOUR
    while hour < WORK_END_HOUR:
        time_str = f"{hour:02d}:00"

        if time_str in booked_times:
            # Зайнятий слот
            row.append(InlineKeyboardButton(text=f"✕ {time_str}", callback_data="cal:ignore"))
        elif is_today and hour <= now.hour:
            # Вже минув час
            row.append(InlineKeyboardButton(text=f"· {time_str}", callback_data="cal:ignore"))
        else:
            row.append(InlineKeyboardButton(text=f"🕐 {time_str}", callback_data=f"time:{time_str}"))

        slot_count += 1
        if slot_count % 3 == 0:
            buttons.append(row)
            row = []

        hour += 1

    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text="◀️ Вибрати іншу дату", callback_data="booking:back_to_calendar")])
    buttons.append([InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_booking_kb() -> InlineKeyboardMarkup:
    """Кнопки підтвердження запису."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Підтвердити", callback_data="booking:confirm"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="booking:cancel_flow"),
        ]
    ])
