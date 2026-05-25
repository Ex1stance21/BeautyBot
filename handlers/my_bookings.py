from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.queries import get_user_active_bookings, cancel_booking
from keyboards.main_menu import get_back_to_menu_kb
from utils.helpers import format_date_ua, format_weekday_ua, format_price

router = Router()


@router.callback_query(F.data == "menu:my_bookings")
async def show_my_bookings(callback: CallbackQuery):
    """Список активних записів користувача."""
    bookings = await get_user_active_bookings(callback.from_user.id)

    if not bookings:
        text = (
            "📋 <b>Мої записи</b>\n\n"
            "У вас поки немає активних записів.\n"
            "Бажаєте записатися? 💅"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Записатися", callback_data="menu:booking")],
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")],
        ])
        await callback.message.edit_text(text, reply_markup=kb)
        await callback.answer()
        return

    text = f"📋 <b>Мої записи</b> ({len(bookings)})\n\n"
    buttons = []

    for b in bookings:
        date_ua = format_date_ua(b["booking_date"])
        weekday = format_weekday_ua(b["booking_date"])
        text += (
            f"{'─' * 25}\n"
            f"{b['emoji']} <b>{b['service_name']}</b>\n"
            f"├ 📅 {date_ua} ({weekday})\n"
            f"├ 🕐 {b['booking_time']}\n"
            f"└ 💰 {format_price(b['service_price'])}\n\n"
        )
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ Скасувати: {b['service_name']} ({b['booking_date']})",
                callback_data=f"cancel_booking:{b['id']}"
            )
        ])

    buttons.append([InlineKeyboardButton(text="📅 Новий запис", callback_data="menu:booking")])
    buttons.append([InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")])

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data.startswith("cancel_booking:"))
async def confirm_cancel(callback: CallbackQuery):
    """Підтвердження скасування запису."""
    booking_id = int(callback.data.split(":")[1])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Так, скасувати", callback_data=f"do_cancel:{booking_id}"),
            InlineKeyboardButton(text="◀️ Ні, повернутися", callback_data="menu:my_bookings"),
        ]
    ])
    await callback.message.edit_text(
        "⚠️ <b>Ви впевнені, що хочете скасувати запис?</b>\n\n"
        "Цю дію не можна буде скасувати.",
        reply_markup=kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("do_cancel:"))
async def do_cancel_booking(callback: CallbackQuery):
    """Скасування запису."""
    booking_id = int(callback.data.split(":")[1])
    await cancel_booking(booking_id)

    await callback.message.edit_text(
        "✅ <b>Запис скасовано</b>\n\n"
        "Ви можете створити новий запис у будь-який час 💅",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Новий запис", callback_data="menu:booking")],
            [InlineKeyboardButton(text="📋 Мої записи", callback_data="menu:my_bookings")],
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")],
        ])
    )
    await callback.answer("✅ Скасовано")
