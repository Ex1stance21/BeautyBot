from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.main_menu import get_back_to_menu_kb
from config import SALON_NAME, SALON_ADDRESS, SALON_PHONE, SALON_INSTAGRAM, SALON_MAPS_LINK

router = Router()


@router.callback_query(F.data == "menu:contacts")
async def show_contacts(callback: CallbackQuery):
    """Контакти салону з посиланням на карту."""
    text = (
        f"📍 <b>Контакти {SALON_NAME}</b>\n\n"
        f"🏠 <b>Адреса:</b>\n{SALON_ADDRESS}\n\n"
        f"📞 <b>Телефон:</b>\n{SALON_PHONE}\n\n"
        f"📸 <b>Instagram:</b>\n{SALON_INSTAGRAM}\n\n"
        f"⏰ <b>Графік роботи:</b>\n"
        f"├ Пн-Пт: 09:00 — 19:00\n"
        f"├ Сб: 10:00 — 18:00\n"
        f"└ Нд: вихідний\n\n"
        f"🗺 <a href='{SALON_MAPS_LINK}'>📌 Відкрити на Google Maps</a>"
    )
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 Показати на карті", callback_data="contacts:map")],
        [InlineKeyboardButton(text="📅 Записатися", callback_data="menu:booking")],
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")],
    ])
    await callback.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
    await callback.answer()


@router.callback_query(F.data == "contacts:map")
async def send_location(callback: CallbackQuery):
    """Надсилає локацію салону."""
    from config import SALON_LATITUDE, SALON_LONGITUDE
    await callback.message.answer_location(
        latitude=SALON_LATITUDE,
        longitude=SALON_LONGITUDE
    )
    await callback.answer("📍 Локацію надіслано!")
