from database.db import get_db
from datetime import datetime


# ═══════════════════════════════════════════
#  ПОСЛУГИ
# ═══════════════════════════════════════════

async def get_all_services():
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM services WHERE is_active = 1 ORDER BY price"
        )
        return await cursor.fetchall()
    finally:
        await db.close()


async def get_service_by_id(service_id: int):
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM services WHERE id = ?", (service_id,)
        )
        return await cursor.fetchone()
    finally:
        await db.close()


async def count_services():
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM services WHERE is_active = 1"
        )
        row = await cursor.fetchone()
        return row["cnt"]
    finally:
        await db.close()


# ═══════════════════════════════════════════
#  ЗАПИСИ (BOOKINGS)
# ═══════════════════════════════════════════

async def create_booking(user_id, user_name, user_phone, service_id, booking_date, booking_time):
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO bookings
               (user_id, user_name, user_phone, service_id, booking_date, booking_time)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, user_name, user_phone, service_id, booking_date, booking_time)
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def get_user_active_bookings(user_id: int):
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT b.*, s.name as service_name, s.price as service_price, s.emoji
               FROM bookings b
               JOIN services s ON b.service_id = s.id
               WHERE b.user_id = ? AND b.status = 'active'
               ORDER BY b.booking_date, b.booking_time""",
            (user_id,)
        )
        return await cursor.fetchall()
    finally:
        await db.close()


async def cancel_booking(booking_id: int):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE id = ?",
            (booking_id,)
        )
        await db.commit()
    finally:
        await db.close()


async def get_booked_times(date_str: str):
    """Повертає список зайнятих часів на дату."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT booking_time FROM bookings WHERE booking_date = ? AND status = 'active'",
            (date_str,)
        )
        rows = await cursor.fetchall()
        return [row["booking_time"] for row in rows]
    finally:
        await db.close()


async def get_bookings_by_date(date_str: str):
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT b.*, s.name as service_name, s.price as service_price, s.emoji
               FROM bookings b
               JOIN services s ON b.service_id = s.id
               WHERE b.booking_date = ? AND b.status = 'active'
               ORDER BY b.booking_time""",
            (date_str,)
        )
        return await cursor.fetchall()
    finally:
        await db.close()


async def get_today_bookings():
    today = datetime.now().strftime("%Y-%m-%d")
    return await get_bookings_by_date(today)


async def get_all_active_bookings():
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT b.*, s.name as service_name, s.price as service_price, s.emoji
               FROM bookings b
               JOIN services s ON b.service_id = s.id
               WHERE b.status = 'active'
               ORDER BY b.booking_date, b.booking_time"""
        )
        return await cursor.fetchall()
    finally:
        await db.close()


async def get_bookings_for_reminder():
    """Записи, яким потрібно надіслати нагадування."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT b.*, s.name as service_name
               FROM bookings b
               JOIN services s ON b.service_id = s.id
               WHERE b.status = 'active' AND b.reminder_sent = 0"""
        )
        return await cursor.fetchall()
    finally:
        await db.close()


async def mark_reminder_sent(booking_id: int):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE bookings SET reminder_sent = 1 WHERE id = ?",
            (booking_id,)
        )
        await db.commit()
    finally:
        await db.close()


# ═══════════════════════════════════════════
#  СТАТИСТИКА
# ═══════════════════════════════════════════

async def get_stats():
    db = await get_db()
    try:
        stats = {}
        cur = await db.execute("SELECT COUNT(*) as cnt FROM bookings WHERE status = 'active'")
        stats["active_bookings"] = (await cur.fetchone())["cnt"]

        cur = await db.execute("SELECT COUNT(*) as cnt FROM bookings WHERE status = 'completed'")
        stats["completed_bookings"] = (await cur.fetchone())["cnt"]

        cur = await db.execute("SELECT COUNT(*) as cnt FROM bookings WHERE status = 'cancelled'")
        stats["cancelled_bookings"] = (await cur.fetchone())["cnt"]

        cur = await db.execute("SELECT COUNT(DISTINCT user_id) as cnt FROM bookings")
        stats["total_clients"] = (await cur.fetchone())["cnt"]

        cur = await db.execute("SELECT COALESCE(SUM(s.price), 0) as total FROM bookings b JOIN services s ON b.service_id = s.id WHERE b.status = 'active'")
        stats["total_revenue"] = (await cur.fetchone())["total"]

        cur = await db.execute("SELECT COALESCE(AVG(rating), 0) as avg FROM reviews")
        stats["avg_rating"] = round((await cur.fetchone())["avg"], 1)

        cur = await db.execute("SELECT COUNT(*) as cnt FROM reviews")
        stats["total_reviews"] = (await cur.fetchone())["cnt"]

        return stats
    finally:
        await db.close()


# ═══════════════════════════════════════════
#  ВІДГУКИ
# ═══════════════════════════════════════════

async def create_review(user_id, user_name, rating, text):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO reviews (user_id, user_name, rating, text) VALUES (?, ?, ?, ?)",
            (user_id, user_name, rating, text)
        )
        await db.commit()
    finally:
        await db.close()


async def get_recent_reviews(limit=10):
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM reviews ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return await cursor.fetchall()
    finally:
        await db.close()


async def get_avg_rating():
    db = await get_db()
    try:
        cursor = await db.execute("SELECT COALESCE(AVG(rating), 0) as avg, COUNT(*) as cnt FROM reviews")
        row = await cursor.fetchone()
        return round(row["avg"], 1), row["cnt"]
    finally:
        await db.close()
