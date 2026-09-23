import aiosqlite


# 1. Создание таблицы при старте
async def init_db():
  async with aiosqlite.connect("coffee_shop.db") as db:
    await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                phone TEXT
            )
        """)
    await db.commit()


# 2. Сохранение нового заказа
async def add_order(user_id: int, name: str, phone: str):
  async with aiosqlite.connect("coffee_shop.db") as db:
    await db.execute(
        "INSERT INTO orders (user_id, name, phone) VALUES (?, ?, ?)",
        (user_id, name, phone),
    )
    await db.commit()


# 3. Чтение всех заказов из базы
async def get_all_orders():
  async with aiosqlite.connect("coffee_shop.db") as db:
    async with db.execute("SELECT * FROM orders") as cursor:
      return await cursor.fetchall()