from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_services_kb(services) -> InlineKeyboardMarkup:
    """Клавіатура зі списком послуг."""
    buttons = []
    for s in services:
        price = int(s["price"]) if s["price"] == int(s["price"]) else s["price"]
        buttons.append([
            InlineKeyboardButton(
                text=f"{s['emoji']} {s['name']} — {price} грн",
                callback_data=f"service:view:{s['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_service_detail_kb(service_id: int) -> InlineKeyboardMarkup:
    """Кнопки деталей послуги."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записатися на цю послугу", callback_data=f"book:service:{service_id}")],
        [InlineKeyboardButton(text="◀️ Назад до послуг", callback_data="menu:services")],
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")],
    ])


async def get_services_for_booking_kb(services) -> InlineKeyboardMarkup:
    """Клавіатура вибору послуги для запису."""
    buttons = []
    for s in services:
        price = int(s["price"]) if s["price"] == int(s["price"]) else s["price"]
        buttons.append([
            InlineKeyboardButton(
                text=f"{s['emoji']} {s['name']} — {price} грн",
                callback_data=f"book:service:{s['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
