from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.queries import (
    get_all_services, get_service_by_id,
    get_booked_times, create_booking
)
from keyboards.services_kb import get_services_for_booking_kb
from keyboards.calendar_kb import get_calendar_kb, get_time_slots_kb, get_confirm_booking_kb
from keyboards.main_menu import get_main_menu
from utils.helpers import format_date_ua, format_weekday_ua, format_price

router = Router()


class BookingStates(StatesGroup):
    choosing_service = State()
    choosing_date = State()
    choosing_time = State()
    entering_name = State()
    entering_phone = State()
    confirming = State()


# ── Крок 1: Вибір послуги ──

@router.callback_query(F.data == "menu:booking")
async def start_booking(callback: CallbackQuery, state: FSMContext):
    """Початок процесу запису — вибір послуги."""
    await state.clear()
    services = await get_all_services()
    text = "📅 <b>Запис на послугу</b>\n\nОберіть послугу 👇"
    kb = await get_services_for_booking_kb(services)
    await callback.message.edit_text(text, reply_markup=kb)
    await state.set_state(BookingStates.choosing_service)
    await callback.answer()


@router.callback_query(F.data.startswith("book:service:"))
async def select_service(callback: CallbackQuery, state: FSMContext):
    """Послугу обрано — показуємо календар."""
    service_id = int(callback.data.split(":")[2])
    service = await get_service_by_id(service_id)

    if not service:
        await callback.answer("❌ Послугу не знайдено", show_alert=True)
        return

    await state.update_data(service_id=service_id, service_name=service["name"], service_price=service["price"])

    text = (
        f"📅 <b>Оберіть дату</b>\n\n"
        f"Послуга: {service['emoji']} <b>{service['name']}</b>\n"
        f"Вартість: <b>{format_price(service['price'])}</b>\n\n"
        f"🔹 Натисніть на дату у календарі\n"
        f"🔹 <b>✕</b> — неділя (вихідний)\n"
        f"🔹 <b>·</b> — минулі дні"
    )
    await callback.message.edit_text(text, reply_markup=get_calendar_kb())
    await state.set_state(BookingStates.choosing_date)
    await callback.answer()


# ── Навігація календарем ──

@router.callback_query(F.data.startswith("cal:prev:"))
async def calendar_prev(callback: CallbackQuery, state: FSMContext):
    """Попередній місяць."""
    _, _, year, month = callback.data.split(":")
    year, month = int(year), int(month)
    month -= 1
    if month < 1:
        month = 12
        year -= 1

    data = await state.get_data()
    service_name = data.get("service_name", "")
    service_price = data.get("service_price", 0)

    text = (
        f"📅 <b>Оберіть дату</b>\n\n"
        f"Послуга: <b>{service_name}</b>\n"
        f"Вартість: <b>{format_price(service_price)}</b>"
    )
    await callback.message.edit_text(text, reply_markup=get_calendar_kb(year, month))
    await callback.answer()


@router.callback_query(F.data.startswith("cal:next:"))
async def calendar_next(callback: CallbackQuery, state: FSMContext):
    """Наступний місяць."""
    _, _, year, month = callback.data.split(":")
    year, month = int(year), int(month)
    month += 1
    if month > 12:
        month = 1
        year += 1

    data = await state.get_data()
    service_name = data.get("service_name", "")
    service_price = data.get("service_price", 0)

    text = (
        f"📅 <b>Оберіть дату</b>\n\n"
        f"Послуга: <b>{service_name}</b>\n"
        f"Вартість: <b>{format_price(service_price)}</b>"
    )
    await callback.message.edit_text(text, reply_markup=get_calendar_kb(year, month))
    await callback.answer()


@router.callback_query(F.data == "cal:ignore")
async def calendar_ignore(callback: CallbackQuery):
    """Ігнорування натискання на порожні/заголовкові кнопки."""
    await callback.answer()


# ── Крок 2: Вибір дати ──

@router.callback_query(F.data.startswith("cal:day:"))
async def select_date(callback: CallbackQuery, state: FSMContext):
    """Дату обрано — показуємо вільні слоти."""
    parts = callback.data.split(":")
    year, month, day = int(parts[2]), int(parts[3]), int(parts[4])
    date_str = f"{year}-{month:02d}-{day:02d}"

    booked = await get_booked_times(date_str)
    await state.update_data(booking_date=date_str)

    data = await state.get_data()
    text = (
        f"🕐 <b>Оберіть час</b>\n\n"
        f"Послуга: <b>{data.get('service_name')}</b>\n"
        f"Дата: <b>{format_date_ua(date_str)}</b> ({format_weekday_ua(date_str)})\n\n"
        f"🟢 Вільно  |  ✕ Зайнято  |  · Минуло"
    )
    kb = await get_time_slots_kb(date_str, booked)
    await callback.message.edit_text(text, reply_markup=kb)
    await state.set_state(BookingStates.choosing_time)
    await callback.answer()


@router.callback_query(F.data == "booking:back_to_calendar")
async def back_to_calendar(callback: CallbackQuery, state: FSMContext):
    """Повернення до календаря."""
    data = await state.get_data()
    text = (
        f"📅 <b>Оберіть дату</b>\n\n"
        f"Послуга: <b>{data.get('service_name')}</b>\n"
        f"Вартість: <b>{format_price(data.get('service_price', 0))}</b>"
    )
    await callback.message.edit_text(text, reply_markup=get_calendar_kb())
    await state.set_state(BookingStates.choosing_date)
    await callback.answer()


# ── Крок 3: Вибір часу ──

@router.callback_query(F.data.startswith("time:"))
async def select_time(callback: CallbackQuery, state: FSMContext):
    """Час обрано — запитуємо ім'я."""
    time_str = callback.data.split(":")[1] + ":" + callback.data.split(":")[2]
    await state.update_data(booking_time=time_str)
    await state.set_state(BookingStates.entering_name)

    data = await state.get_data()
    text = (
        f"👤 <b>Введіть ваше ім'я</b>\n\n"
        f"Послуга: <b>{data.get('service_name')}</b>\n"
        f"Дата: <b>{format_date_ua(data.get('booking_date'))}</b>\n"
        f"Час: <b>{time_str}</b>\n\n"
        f"Напишіть ваше ім'я 👇"
    )
    await callback.message.edit_text(text)
    await callback.answer()


# ── Крок 4: Введення імені ──

@router.message(BookingStates.entering_name)
async def enter_name(message: Message, state: FSMContext):
    """Ім'я введено — запитуємо телефон."""
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("❌ Будь ласка, введіть коректне ім'я (мінімум 2 символи)")
        return

    await state.update_data(user_name=name)
    await state.set_state(BookingStates.entering_phone)
    await message.answer(
        f"📱 <b>Введіть ваш номер телефону</b>\n\n"
        f"Наприклад: <code>+380991234567</code>"
    )


# ── Крок 5: Введення телефону ──

@router.message(BookingStates.entering_phone)
async def enter_phone(message: Message, state: FSMContext):
    """Телефон введено — показуємо підтвердження."""
    phone = message.text.strip()
    if len(phone) < 10:
        await message.answer("❌ Будь ласка, введіть коректний номер телефону")
        return

    await state.update_data(user_phone=phone)
    await state.set_state(BookingStates.confirming)

    data = await state.get_data()
    text = (
        "📋 <b>Перевірте дані запису</b>\n\n"
        f"┌ 💅 Послуга: <b>{data['service_name']}</b>\n"
        f"├ 💰 Вартість: <b>{format_price(data['service_price'])}</b>\n"
        f"├ 📅 Дата: <b>{format_date_ua(data['booking_date'])}</b>\n"
        f"├ 🕐 Час: <b>{data['booking_time']}</b>\n"
        f"├ 👤 Ім'я: <b>{data['user_name']}</b>\n"
        f"└ 📱 Телефон: <b>{data['user_phone']}</b>\n\n"
        "Все вірно? 👇"
    )
    await message.answer(text, reply_markup=get_confirm_booking_kb())


# ── Крок 6: Підтвердження ──

@router.callback_query(F.data == "booking:confirm")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    """Підтвердження запису — зберігаємо в БД."""
    data = await state.get_data()

    booking_id = await create_booking(
        user_id=callback.from_user.id,
        user_name=data["user_name"],
        user_phone=data["user_phone"],
        service_id=data["service_id"],
        booking_date=data["booking_date"],
        booking_time=data["booking_time"]
    )

    text = (
        "✅ <b>Запис успішно створено!</b>\n\n"
        f"📌 Номер запису: <b>#{booking_id}</b>\n"
        f"┌ 💅 {data['service_name']}\n"
        f"├ 📅 {format_date_ua(data['booking_date'])}\n"
        f"├ 🕐 {data['booking_time']}\n"
        f"└ 💰 {format_price(data['service_price'])}\n\n"
        "⏰ Ми нагадаємо вам за 2 години до візиту!\n"
        "Дякуємо, чекаємо на вас! 💕"
    )
    await callback.message.edit_text(text, reply_markup=get_main_menu())
    await state.clear()
    await callback.answer("✅ Записано!")


@router.callback_query(F.data == "booking:cancel_flow")
async def cancel_booking_flow(callback: CallbackQuery, state: FSMContext):
    """Скасування процесу запису."""
    await state.clear()
    await callback.message.edit_text(
        "❌ Запис скасовано.\n\nОберіть дію в меню 👇",
        reply_markup=get_main_menu()
    )
    await callback.answer()
