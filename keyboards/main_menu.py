from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> InlineKeyboardMarkup:
    """Головне меню бота."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💅 Послуги та ціни", callback_data="menu:services")],
        [InlineKeyboardButton(text="📅 Записатися", callback_data="menu:booking")],
        [InlineKeyboardButton(text="📋 Мої записи", callback_data="menu:my_bookings")],
        [
            InlineKeyboardButton(text="📸 Портфоліо", callback_data="menu:portfolio"),
            InlineKeyboardButton(text="⭐ Відгуки", callback_data="menu:reviews"),
        ],
        [InlineKeyboardButton(text="📍 Контакти", callback_data="menu:contacts")],
        [InlineKeyboardButton(text="ℹ️ Про салон", callback_data="menu:about")],
    ])


def get_back_to_menu_kb() -> InlineKeyboardMarkup:
    """Кнопка повернення до головного меню."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")]
    ])
