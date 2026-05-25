from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS
from database.queries import (
    get_today_bookings, get_all_active_bookings,
    get_stats, get_recent_reviews
)
from keyboards.admin_kb import get_admin_menu_kb, get_admin_back_kb
from utils.helpers import format_date_ua, format_price, stars_emoji

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Адмін-панель."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас немає доступу до адмін-панелі.")
        return

    text = (
        "🔐 <b>Адмін-панель</b>\n\n"
        "Оберіть дію 👇"
    )
    await message.answer(text, reply_markup=get_admin_menu_kb())


@router.callback_query(F.data == "admin:panel")
async def admin_panel(callback: CallbackQuery):
    """Повернення до адмін-панелі."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Немає доступу", show_alert=True)
        return

    text = "🔐 <b>Адмін-панель</b>\n\nОберіть дію 👇"
    await callback.message.edit_text(text, reply_markup=get_admin_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "admin:today")
async def admin_today(callback: CallbackQuery):
    """Записи на сьогодні."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Немає доступу", show_alert=True)
        return

    bookings = await get_today_bookings()

    if not bookings:
        text = "📊 <b>Записи на сьогодні</b>\n\n😴 На сьогодні записів немає."
    else:
        text = f"📊 <b>Записи на сьогодні</b> ({len(bookings)})\n\n"
        for b in bookings:
            text += (
                f"🕐 <b>{b['booking_time']}</b> — {b['emoji']} {b['service_name']}\n"
                f"├ 👤 {b['user_name']} | 📱 {b['user_phone']}\n"
                f"└ 💰 {format_price(b['service_price'])}\n\n"
            )

    await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()


@router.callback_query(F.data == "admin:all")
async def admin_all(callback: CallbackQuery):
    """Всі активні записи."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Немає доступу", show_alert=True)
        return

    bookings = await get_all_active_bookings()

    if not bookings:
        text = "📅 <b>Активні записи</b>\n\n😴 Немає активних записів."
    else:
        text = f"📅 <b>Всі активні записи</b> ({len(bookings)})\n\n"
        for b in bookings:
            text += (
                f"📅 <b>{format_date_ua(b['booking_date'])}</b> о {b['booking_time']}\n"
                f"├ {b['emoji']} {b['service_name']}\n"
                f"├ 👤 {b['user_name']} | 📱 {b['user_phone']}\n"
                f"└ 💰 {format_price(b['service_price'])}\n\n"
            )

    await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    """Статистика."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Немає доступу", show_alert=True)
        return

    stats = await get_stats()
    text = (
        "📈 <b>Статистика</b>\n\n"
        f"📊 <b>Записи:</b>\n"
        f"├ ✅ Активні: <b>{stats['active_bookings']}</b>\n"
        f"├ ✔️ Виконані: <b>{stats['completed_bookings']}</b>\n"
        f"└ ❌ Скасовані: <b>{stats['cancelled_bookings']}</b>\n\n"
        f"👥 <b>Клієнти:</b> {stats['total_clients']}\n"
        f"💰 <b>Очікувана виручка:</b> {format_price(stats['total_revenue'])}\n\n"
        f"⭐ <b>Рейтинг:</b> {stats['avg_rating']}/5 ({stats['total_reviews']} відгуків)"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()


@router.callback_query(F.data == "admin:reviews")
async def admin_reviews(callback: CallbackQuery):
    """Відгуки для адміна."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Немає доступу", show_alert=True)
        return

    reviews = await get_recent_reviews(10)

    if not reviews:
        text = "⭐ <b>Відгуки</b>\n\n😴 Поки немає відгуків."
    else:
        text = "⭐ <b>Останні відгуки</b>\n\n"
        for r in reviews:
            name = r["user_name"] or "Анонім"
            text += (
                f"{stars_emoji(r['rating'])} <b>{name}</b> ({r['created_at'][:10]})\n"
            )
            if r["text"]:
                text += f"💬 <i>{r['text']}</i>\n"
            text += "\n"

    await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()
