import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeDefault,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
   )

# Импортируем функции из db.py
from db import add_order, get_all_orders, init_db

TOKEN = "8833556031:AAGktjcks61HBOCiRW6xSuPG_gnIJRJ0H3s"
ADMIN_ID = 6038727126

bot = Bot(token=TOKEN)
dp = Dispatcher()


class OrderForm(StatesGroup):
  name = State()
  phone = State()


# Главное меню
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="☕ Меню"), KeyboardButton(text="📍 Адрес")],
        [KeyboardButton(text="📞 Связь с админом")],
        [KeyboardButton(text="📞 зделать заказ")],
    ],
    resize_keyboard=True,
)

# Кнопка запроса контакта
phone_req_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Отправить свой номер", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

admin_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(
            text="Написать в WhatsApp", url="https://wa.me/77000000000"
        )
    ]]
)


@dp.message(Command("start"))
async def start(message: types.Message):
  await message.answer(
      "Добро пожаловать в кофейню! Выберите раздел:", reply_markup=main_kb
  )


# ----------------- РАБОТА С FSM -----------------


@dp.message(F.text == "📞 зделать заказ")
async def start_order(message: types.Message, state: FSMContext):
  await state.set_state(OrderForm.name)
  await message.answer("Отлично! Как к вам обращаться? Напишите ваше имя:")


@dp.message(OrderForm.name, F.text)
async def process_name(message: types.Message, state: FSMContext):
  await state.update_data(name=message.text)
  await state.set_state(OrderForm.phone)
  await message.answer(
      "Супер! Нажмите кнопку ниже или введите номер вручную:",
      reply_markup=phone_req_kb,
  )


@dp.message(OrderForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
  if message.contact:
    phone = message.contact.phone_number
  else:
    phone = message.text

  clean_phone = "".join(c for c in phone if c.isdigit() or c == "+")

  if not clean_phone or len(clean_phone) < 5:
    await message.answer(
        "Пожалуйста, введите корректный номер телефона (например:"
        " +77071234567):"
    )
    return

  user_data = await state.get_data()
  name = user_data.get("name", "Не указано")

  # 1. Сохраняем заказ в базу SQLite
  await add_order(user_id=message.from_user.id, name=name, phone=clean_phone)

  # 2. Выводим все заказы из базы в консоль PyCharm
  all_orders = await get_all_orders()
  print("\n--- 📦 ВСЕ ЗАКАЗЫ ИЗ БАЗЫ DANA ---")
  print(all_orders)
  print("-----------------------------------\n")

  # Кнопка для админа
  admin_lead_kb = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="💬 Написать клиенту",
                  url=f"tg://user?id={message.from_user.id}",
              )
          ],
          [InlineKeyboardButton(text="✅ Принято", callback_data="order_done")],
      ]
  )

  # Отправляем заявку админу
  await message.bot.send_message(
      chat_id=ADMIN_ID,
      text=(
          f"🚨 **НОВАЯ ЗАЯВКА В КОФЕЙНЮ!**\n\n👤 Имя: {name}\n📞 Телефон:"
          f" `{clean_phone}`"
      ),
      reply_markup=admin_lead_kb,
      parse_mode="Markdown",
  )

  # Ответ клиенту
  await message.answer(
      f"✅ Заявка принята!\n\nВаше имя: {name}\nВаш телефон:"
      f" {clean_phone}\n\nМенеджер свяжется с вами!",
      reply_markup=main_kb,
  )

  await state.clear()


@dp.message(Command("orders"))
async def show_orders(message: types.Message):
  # 🔒 Защита: если пишет НЕ админ — игнорируем или шлем отказ
  if message.from_user.id != ADMIN_ID:
    await message.answer("⛔ У вас нет доступа к этой команде.")
    return

  all_orders = await get_all_orders()

  if not all_orders:
    await message.answer("Заказов пока нет!")
    return

  text = "📦 **Список всех заказов:**\n\n"
  for order in all_orders:
    order_id, user_id, name, phone = order
    text += f"🔹 Заказ #{order_id} | Имя: {name} | Тел: {phone}\n"

  await message.answer(text, parse_mode="Markdown")


# ----------------- ОБЫЧНОЕ МЕНЮ -----------------


@dp.message()
async def menu_handler(message: types.Message):
  text = message.text.lower()
  if text == "☕ меню":
    await message.answer(
        "1. Капучино — 1000 ₸\n2. Латте — 1200 ₸\n3. Чизкейк — 1500 ₸"
    )
  elif text == "📍 адрес":
    await message.answer("Мы находимся по адресу: ул. Абая, 150")
  elif text == "📞 связь с админом":
    await message.answer(
        "Для оперативной связи нажмите кнопку ниже:",
        reply_markup=admin_inline_kb,
    )
  else:
    await message.answer("Воспользуйтесь кнопками меню 👇")


# ----------------- ЗАПУСК БОТА -----------------


async def set_main_menu(bot: Bot):
  # 1. Меню для ОБЫЧНЫХ пользователей (только старт)
  user_commands = [
      BotCommand(
          command="start", description="Запустить бота / Главное меню"
      ),
  ]
  await bot.set_my_commands(
      user_commands, scope=BotCommandScopeDefault()
  )

  # 2. Меню ТОЛЬКО ДЛЯ АДМИНА (старт + просмотр заказов)
  admin_commands = [
      BotCommand(
          command="start", description="Запустить бота / Главное меню"
      ),
      BotCommand(command="orders", description="📦 Просмотр заказов (Админ)"),
  ]
  await bot.set_my_commands(
      admin_commands, scope=BotCommandScopeChat(chat_id=ADMIN_ID)
  )


async def main():
  await init_db()
  await set_main_menu(bot)
  print("бот запущен")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())