from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_menu_kb() -> InlineKeyboardMarkup:
    """Адмін-панель."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Записи на сьогодні", callback_data="admin:today")],
        [InlineKeyboardButton(text="📅 Всі активні записи", callback_data="admin:all")],
        [InlineKeyboardButton(text="📈 Статистика", callback_data="admin:stats")],
        [InlineKeyboardButton(text="⭐ Відгуки клієнтів", callback_data="admin:reviews")],
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")],
    ])


def get_admin_back_kb() -> InlineKeyboardMarkup:
    """Повернення до адмін-панелі."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Адмін-панель", callback_data="admin:panel")],
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")],
    ])
