from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# ── Демо-портфоліо (опис робіт) ──
PORTFOLIO_ITEMS = [
    {
        "title": "🌸 Ніжний весняний дизайн",
        "description": "Пастельні відтінки з квітковим орнаментом. Гель-лак + ручний розпис.",
        "tags": "#весна #квіти #пастель",
    },
    {
        "title": "💎 Французький манікюр Deluxe",
        "description": "Класичний френч з тонкою лінією усмішки та мікро-стразами Swarovski.",
        "tags": "#френч #класика #стрази",
    },
    {
        "title": "🔥 Яскравий літній градієнт",
        "description": "Плавний перехід від коралового до фуксії. Омбре-техніка.",
        "tags": "#градієнт #омбре #літо",
    },
    {
        "title": "🖤 Мінімалістичний геометричний",
        "description": "Нюдова база з геометричними лініями. Сучасний та стильний.",
        "tags": "#мінімалізм #геометрія #нюд",
    },
    {
        "title": "✨ Святковий дизайн з фольгою",
        "description": "Відбитки фольги на темній базі. Ідеально для вечірок!",
        "tags": "#святковий #фольга #вечірній",
    },
    {
        "title": "🌿 Ботанічний принт",
        "description": "Натуральні відтінки з ручним розписом листочків та гілок.",
        "tags": "#ботаніка #природа #розпис",
    },
]


def get_portfolio_kb(index: int) -> InlineKeyboardMarkup:
    """Навігація по портфоліо."""
    buttons = []
    nav = []

    if index > 0:
        nav.append(InlineKeyboardButton(text="◀️ Попередня", callback_data=f"portfolio:{index - 1}"))

    nav.append(InlineKeyboardButton(text=f"{index + 1}/{len(PORTFOLIO_ITEMS)}", callback_data="cal:ignore"))

    if index < len(PORTFOLIO_ITEMS) - 1:
        nav.append(InlineKeyboardButton(text="Наступна ▶️", callback_data=f"portfolio:{index + 1}"))

    buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="📅 Записатися", callback_data="menu:booking")])
    buttons.append([InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "menu:portfolio")
async def show_portfolio(callback: CallbackQuery):
    """Початок перегляду портфоліо."""
    item = PORTFOLIO_ITEMS[0]
    text = (
        "📸 <b>Портфоліо наших робіт</b>\n\n"
        f"<b>{item['title']}</b>\n\n"
        f"📝 {item['description']}\n\n"
        f"🏷 {item['tags']}\n\n"
        f"<i>Гортайте для перегляду інших робіт →</i>"
    )
    await callback.message.edit_text(text, reply_markup=get_portfolio_kb(0))
    await callback.answer()


@router.callback_query(F.data.startswith("portfolio:"))
async def navigate_portfolio(callback: CallbackQuery):
    """Навігація по портфоліо."""
    index = int(callback.data.split(":")[1])
    if index < 0 or index >= len(PORTFOLIO_ITEMS):
        await callback.answer()
        return

    item = PORTFOLIO_ITEMS[index]
    text = (
        "📸 <b>Портфоліо наших робіт</b>\n\n"
        f"<b>{item['title']}</b>\n\n"
        f"📝 {item['description']}\n\n"
        f"🏷 {item['tags']}"
    )
    await callback.message.edit_text(text, reply_markup=get_portfolio_kb(index))
    await callback.answer()
