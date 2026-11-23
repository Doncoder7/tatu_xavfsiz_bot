import aiosqlite
from config import DB_NAME

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Foydalanuvchilar (talabalar va mas'ullar)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                role TEXT DEFAULT 'student',
                staff_category TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Murojaatlar (Tickets)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                staff_id INTEGER,
                category TEXT NOT NULL,
                status TEXT DEFAULT 'OPEN',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP
            )
        """)
        
        # Xabarlar mappingi (Mas'ul xabarga reply qilganda talabani topish uchun)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS message_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                staff_msg_id INTEGER NOT NULL,
                staff_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL
            )
        """)
        await db.commit()

async def register_user(user_id: int, role: str = 'student', staff_category: str = None, full_name: str = None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users (user_id, role, staff_category, full_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                role=excluded.role,
                staff_category=excluded.staff_category,
                full_name=excluded.full_name
        """, (user_id, role, staff_category, full_name))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_active_staff_by_category(category: str):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE role = 'staff' AND staff_category = ? LIMIT 1",
            (category,)
        ) as cursor:
            return await cursor.fetchone()

async def get_all_staff_positions():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT staff_category, full_name, user_id FROM users WHERE role = 'staff'") as cursor:
            rows = await cursor.fetchall()
            return {row['staff_category']: row for row in rows}

async def unregister_staff(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users 
            SET role = 'student', staff_category = NULL 
            WHERE user_id = ?
        """, (user_id,))
        await db.commit()

async def create_ticket(student_id: int, category: str, staff_id: int = None):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            INSERT INTO tickets (student_id, staff_id, category, status)
            VALUES (?, ?, ?, ?)
        """, (student_id, staff_id, category, 'ASSIGNED' if staff_id else 'OPEN'))
        await db.commit()
        return cursor.lastrowid

async def get_active_student_ticket(student_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM tickets 
            WHERE student_id = ? AND status IN ('OPEN', 'ASSIGNED')
            ORDER BY id DESC LIMIT 1
        """, (student_id,)) as cursor:
            return await cursor.fetchone()

async def get_active_ticket_for_staff(staff_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM tickets 
            WHERE staff_id = ? AND status = 'ASSIGNED'
            ORDER BY id DESC
        """, (staff_id,)) as cursor:
            return await cursor.fetchall()


async def get_ticket_by_id(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)) as cursor:
            return await cursor.fetchone()

async def close_ticket(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE tickets 
            SET status = 'CLOSED', closed_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (ticket_id,))
        await db.commit()

async def save_message_mapping(ticket_id: int, staff_msg_id: int, staff_id: int, student_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO message_mappings (ticket_id, staff_msg_id, staff_id, student_id)
            VALUES (?, ?, ?, ?)
        """, (ticket_id, staff_msg_id, staff_id, student_id))
        await db.commit()

async def get_mapping_by_staff_msg(staff_msg_id: int, staff_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM message_mappings 
            WHERE staff_msg_id = ? AND staff_id = ?
            ORDER BY id DESC LIMIT 1
        """, (staff_msg_id, staff_id)) as cursor:
            return await cursor.fetchone()
