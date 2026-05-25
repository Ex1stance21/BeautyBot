from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.queries import get_all_services, get_service_by_id
from keyboards.services_kb import get_services_kb, get_service_detail_kb
from utils.helpers import format_price

router = Router()


@router.callback_query(F.data == "menu:services")
async def show_services(callback: CallbackQuery):
    """Каталог послуг."""
    services = await get_all_services()
    text = (
        "💅 <b>Наші послуги та ціни</b>\n\n"
        "Оберіть послугу для детальної інформації 👇"
    )
    kb = await get_services_kb(services)
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("service:view:"))
async def show_service_detail(callback: CallbackQuery):
    """Деталі послуги."""
    service_id = int(callback.data.split(":")[2])
    service = await get_service_by_id(service_id)

    if not service:
        await callback.answer("❌ Послугу не знайдено", show_alert=True)
        return

    text = (
        f"{service['emoji']} <b>{service['name']}</b>\n\n"
        f"📝 {service['description']}\n\n"
        f"💰 Вартість: <b>{format_price(service['price'])}</b>\n"
        f"⏱ Тривалість: <b>{service['duration_minutes']} хв</b>\n\n"
        f"Бажаєте записатися? 👇"
    )
    await callback.message.edit_text(text, reply_markup=get_service_detail_kb(service_id))
    await callback.answer()
