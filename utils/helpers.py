from datetime import datetime


def format_date_ua(date_str: str) -> str:
    """Форматує дату '2026-05-25' -> '25 травня 2026'."""
    months = {
        1: "січня", 2: "лютого", 3: "березня", 4: "квітня",
        5: "травня", 6: "червня", 7: "липня", 8: "серпня",
        9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня"
    }
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.day} {months[dt.month]} {dt.year}"


def format_weekday_ua(date_str: str) -> str:
    """Повертає день тижня українською."""
    days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return days[dt.weekday()]


def format_price(price: float) -> str:
    """Форматує ціну: 350.0 -> '350 грн'."""
    if price == int(price):
        return f"{int(price)} грн"
    return f"{price:.0f} грн"


def stars_emoji(rating: int) -> str:
    """Повертає зірочки: 4 -> '⭐⭐⭐⭐'."""
    return "⭐" * rating


def get_month_name_ua(month: int) -> str:
    """Повертає назву місяця: 5 -> 'Травень'."""
    names = {
        1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень",
        5: "Травень", 6: "Червень", 7: "Липень", 8: "Серпень",
        9: "Вересень", 10: "Жовтень", 11: "Листопад", 12: "Грудень"
    }
    return names[month]
