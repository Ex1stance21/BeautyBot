from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import get_main_menu, get_back_to_menu_kb
from config import SALON_NAME

router = Router()

WELCOME_TEXT = (
    f"👋 <b>Ласкаво просимо до {SALON_NAME}!</b>\n\n"
    "Я — ваш персональний помічник для запису\n"
    "на манікюр та інші послуги 💅\n\n"
    "🔹 Переглядайте <b>послуги та ціни</b>\n"
    "🔹 Записуйтесь <b>онлайн</b> на зручний час\n"
    "🔹 Переглядайте <b>портфоліо</b> робіт\n"
    "🔹 Залишайте <b>відгуки</b>\n\n"
    "Оберіть потрібний пункт меню 👇"
)

ABOUT_TEXT = (
    f"✨ <b>{SALON_NAME}</b>\n\n"
    "Ми — сучасний салон краси, який спеціалізується\n"
    "на манікюрі та догляді за нігтями.\n\n"
    "🏆 <b>Наші переваги:</b>\n"
    "├ 💎 Преміум матеріали\n"
    "├ 👩‍🎨 Досвідчені майстри\n"
    "├ 🧹 Стерильність інструментів\n"
    "├ ☕ Безкоштовний чай/кава\n"
    "└ 🅿️ Зручна парковка\n\n"
    "⏰ <b>Графік роботи:</b>\n"
    "├ Пн-Пт: 09:00 — 19:00\n"
    "├ Сб: 10:00 — 18:00\n"
    "└ Нд: вихідний\n\n"
    "Запишіться прямо зараз! 👇"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Команда /start — привітання та головне меню."""
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=get_main_menu())


@router.callback_query(F.data == "menu:main")
async def go_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Повернення до головного меню."""
    await state.clear()
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=get_main_menu())
    await callback.answer()


@router.callback_query(F.data == "menu:about")
async def show_about(callback: CallbackQuery):
    """Інформація про салон."""
    await callback.message.edit_text(ABOUT_TEXT, reply_markup=get_back_to_menu_kb())
    await callback.answer()
