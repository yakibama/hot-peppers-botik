import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from aiogram.filters import Command

# -------------------- CONFIG --------------------
BOT_TOKEN = "...."   # твой токен
GROUP_CHAT_ID = -1002708491399     # твоя группа

CLOUD_LINKS = {
    "photo": "https://mega.nz/file/b5xxmBgQ#lKfS_bi3hxj8ahiQ7vX2uBnW15gd3041caD2xkeOgFA",
    "video": "https://mega.nz/folder/OAs0ESQL#FkZD8b9wl5cMwi2Zm2rheA",
    "premium": "https://mega.nz/folder/OAs0ESQL#FkZD8b9wl5cMwi2Zm2rheA"
}

PRICES = {
    "photo": {"amount": 15, "label": "Фото — 15⭐"},
    "video": {"amount": 25, "label": "Видео — 25⭐"},
    "premium": {"amount": 50, "label": "Премиум — 50⭐"},
}

# ------------------------------------------------

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Фото — 15⭐", callback_data="buy_photo")],
        [InlineKeyboardButton(text="🎬 Видео — 25⭐", callback_data="buy_video")],
        [InlineKeyboardButton(text="👑 Премиум — 50⭐", callback_data="buy_premium")]
    ])


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    text = (
        "🌶️ Добро пожаловать в *Hot Peppers!*\n\n"
        "Здесь вы найдете коллекции премиум-фото и видео.\n\n"
        "🎯 Доступные коллекции:\n"
        "• Фото — 15⭐\n"
        "• Видео — 25⭐\n"
        "• Премиум — 50⭐"
    )
    await message.answer(text, reply_markup=main_menu(), parse_mode="Markdown")

    try:
        await bot.send_message(
            GROUP_CHAT_ID,
            f"👋 Новый пользователь: @{message.from_user.username or 'Без ника'} "
            f"(id {message.from_user.id})"
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке в группу: {e}")


async def send_invoice(message: types.Message, item_key: str):
    item = PRICES[item_key]
    await bot.send_invoice(
        chat_id=message.chat.id,
        title=f"{item['label']}",
        description=f"Оплата за {item['label']} в Hot Peppers 🌶️",
        payload=f"buy_{item_key}",
        provider_token="",  # Telegram Stars не требует токена
        currency="XTR",
        prices=[LabeledPrice(label=item['label'], amount=item['amount'])],
    )


@dp.callback_query(lambda c: c.data and c.data.startswith("buy_"))
async def process_buy(callback_query: types.CallbackQuery):
    item_key = callback_query.data.split("_")[1]
    await send_invoice(callback_query.message, item_key)


@dp.pre_checkout_query()
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message(lambda m: m.successful_payment is not None)
async def successful_payment(message: types.Message):
    pay = message.successful_payment
    payload = pay.invoice_payload.replace("buy_", "")
    link = CLOUD_LINKS.get(payload, "Ссылка не установлена")

    await message.answer(f"✅ Оплата прошла успешно!\nВот ваша ссылка: {link}")

    try:
        await bot.send_message(
            GROUP_CHAT_ID,
            f"💰 Оплата от @{message.from_user.username or 'Без ника'} "
            f"(id {message.from_user.id}) — {payload} ({pay.total_amount}⭐)"
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке оплаты в группу: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
