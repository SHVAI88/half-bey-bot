from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from config import API_TOKEN, ADMIN_IDS
from data import products, carts, save_products, save_carts
import json

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛍 Каталог"))
    kb.add(KeyboardButton("🛒 Корзина"))
    return kb


@dp.message_handler(commands=["start"])
async def cmd_start(msg: types.Message):
    # Удаляем клавиатуру
    await msg.answer("...", reply_markup=ReplyKeyboardRemove())

    # Небольшая задержка (Telegram UI успевает убрать клаву)
    await bot.send_chat_action(msg.chat.id, action="typing")

    # Отправляем чистое меню
    await msg.answer("Добро пожаловать 👋", reply_markup=main_menu())


@dp.message_handler(lambda m: m.text == "🛍 Каталог")
async def show_catalog(msg: types.Message):
    if not products:
        await msg.answer("Каталог пока пуст.")
        return

    for i, item in enumerate(products):
        caption = f"🧢 {item['name']}\n{item['description']}\n💵 Цена: {item['price']}BYN\n\nЧтобы купить: напиши `купить {i}`"
        await bot.send_photo(msg.chat.id, item['photo'], caption=caption, parse_mode="Markdown")

@dp.message_handler(lambda m: m.text == "🛒 Корзина")
async def show_cart(msg: types.Message):
    user_id = str(msg.from_user.id)
    cart = carts.get(user_id, [])
    if not cart:
        await msg.answer("🧺 Ваша корзина пуста.")
        return

    text = "🛒 Ваша корзина:\n"
    total = 0
    for i, item in enumerate(cart):
        text += f"{i+1}. {item['name']} — {item['price']}BYN\n"
        total += item['price']
    text += f"\nИтого: {total}BYN"
    text += f"\n\n🔁 Отправьте это сообщение: @{msg.from_user.username or 'без_юзернейма'}"
    await msg.answer(text)

from data import save_products, save_carts  # не забудь

@dp.message_handler(lambda m: m.text.startswith("купить "))
async def buy_item(msg: types.Message):
    user_id = str(msg.from_user.id)
    try:
        index = int(msg.text.split()[1])
        item = products[index]
        carts.setdefault(user_id, []).append(item)
        save_carts()
        await msg.answer(f"✅ Товар «{item['name']}» добавлен в корзину.")
    except (IndexError, ValueError):
        await msg.answer("❌ Неверный номер товара. Пример: купить 0")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo_add(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        return

    if not msg.caption:
        await msg.answer("❗ Введите описание в подписи к фото. Пример:\nКроссовки\nОписание\nЦена:120")
        return

    lines = msg.caption.strip().split('\n')
    if len(lines) < 2:
        await msg.answer("❌ Не хватает описания. Последняя строка — обязательно `Цена:120`")
        return

    try:
        price_line = lines[-1]
        price = int(price_line.replace("Цена:", "").strip())
    except:
        await msg.answer("❌ Последняя строка должна быть вида: `Цена:120`")
        return

    name = lines[0]
    description = "\n".join(lines[1:-1])
    photo_id = msg.photo[-1].file_id

    products.append({
        "name": name,
        "description": description,
        "price": price,
        "photo": photo_id
    })
    save_products()

    await msg.answer(f"✅ Товар «{name}» добавлен.")

@dp.message_handler(commands=['delete'])
async def delete_product(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        return

    try:
        _, index = msg.text.split()
        index = int(index)
        removed = products.pop(index)
        save_products()
        await msg.answer(f"❌ Товар «{removed['name']}» удалён.")
    except:
        await msg.answer("❌ Используй: /delete 0")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
