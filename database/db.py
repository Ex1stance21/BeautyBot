import aiosqlite
from config import DB_PATH


async def init_db():
    """Ініціалізація бази даних — створення таблиць."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                duration_minutes INTEGER NOT NULL DEFAULT 60,
                emoji TEXT DEFAULT '💅',
                is_active BOOLEAN DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_name TEXT,
                user_phone TEXT,
                service_id INTEGER NOT NULL,
                booking_date TEXT NOT NULL,
                booking_time TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                reminder_sent BOOLEAN DEFAULT 0,
                FOREIGN KEY (service_id) REFERENCES services(id)
            );

            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_name TEXT,
                rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                text TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );
        """)
        await db.commit()


async def get_db():
    """Отримати з'єднання з БД (row_factory = aiosqlite.Row)."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db
