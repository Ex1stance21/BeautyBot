from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.queries import create_review, get_recent_reviews, get_avg_rating
from utils.helpers import stars_emoji

router = Router()


class ReviewStates(StatesGroup):
    entering_rating = State()
    entering_text = State()


@router.callback_query(F.data == "menu:reviews")
async def show_reviews(callback: CallbackQuery):
    """Відображення відгуків."""
    reviews = await get_recent_reviews(5)
    avg, total = await get_avg_rating()

    if total == 0:
        text = (
            "⭐ <b>Відгуки</b>\n\n"
            "Поки немає відгуків.\n"
            "Будьте першим! 😊"
        )
    else:
        text = (
            f"⭐ <b>Відгуки клієнтів</b>\n\n"
            f"📊 Середній рейтинг: {stars_emoji(round(avg))} <b>{avg}/5</b> ({total} відгуків)\n\n"
        )
        for r in reviews:
            name = r["user_name"] or "Анонім"
            text += (
                f"{'─' * 25}\n"
                f"👤 <b>{name}</b>\n"
                f"{stars_emoji(r['rating'])} ({r['rating']}/5)\n"
            )
            if r["text"]:
                text += f"💬 <i>{r['text']}</i>\n"
            text += f"📅 {r['created_at'][:10]}\n\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Залишити відгук", callback_data="review:start")],
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")],
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "review:start")
async def start_review(callback: CallbackQuery, state: FSMContext):
    """Початок залишення відгуку — вибір рейтингу."""
    text = (
        "✍️ <b>Залишити відгук</b>\n\n"
        "Оцініть наш сервіс від 1 до 5 зірок 👇"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 ⭐", callback_data="review:rate:1"),
            InlineKeyboardButton(text="2 ⭐", callback_data="review:rate:2"),
            InlineKeyboardButton(text="3 ⭐", callback_data="review:rate:3"),
            InlineKeyboardButton(text="4 ⭐", callback_data="review:rate:4"),
            InlineKeyboardButton(text="5 ⭐", callback_data="review:rate:5"),
        ],
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu:main")],
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await state.set_state(ReviewStates.entering_rating)
    await callback.answer()


@router.callback_query(F.data.startswith("review:rate:"), ReviewStates.entering_rating)
async def select_rating(callback: CallbackQuery, state: FSMContext):
    """Рейтинг обрано — запитуємо текст."""
    rating = int(callback.data.split(":")[2])
    await state.update_data(rating=rating)
    await state.set_state(ReviewStates.entering_text)

    text = (
        f"Ваша оцінка: {stars_emoji(rating)}\n\n"
        f"💬 Напишіть ваш відгук (або надішліть <b>/skip</b>, щоб пропустити)"
    )
    await callback.message.edit_text(text)
    await callback.answer()


@router.message(ReviewStates.entering_text)
async def enter_review_text(message: Message, state: FSMContext):
    """Текст відгуку введено — зберігаємо."""
    data = await state.get_data()
    review_text = None if message.text == "/skip" else message.text.strip()

    user_name = message.from_user.full_name or "Анонім"
    await create_review(
        user_id=message.from_user.id,
        user_name=user_name,
        rating=data["rating"],
        text=review_text
    )

    text = (
        "✅ <b>Дякуємо за ваш відгук!</b>\n\n"
        f"Ваша оцінка: {stars_emoji(data['rating'])}\n"
    )
    if review_text:
        text += f"💬 {review_text}\n"
    text += "\nМи цінуємо вашу думку! 💕"

    from keyboards.main_menu import get_main_menu
    await message.answer(text, reply_markup=get_main_menu())
    await state.clear()
