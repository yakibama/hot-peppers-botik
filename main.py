import os
import json
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice

BOT_TOKEN = os.getenv("BOT_TOKEN")  # 🔥 Токен ТІЛЬКИ з Environment Variables
GROUP_CHAT_ID = -5088058912

# ---------------- JSON SYSTEM ----------------

REF_FILE = "referrals.json"

if not os.path.exists(REF_FILE):
    with open(REF_FILE, "w") as f:
        json.dump({}, f)


def load_refs():
    with open(REF_FILE, "r") as f:
        return json.load(f)


def save_refs(data):
    with open(REF_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- MENU ----------------

def main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Фото — 15⭐", callback_data="buy_photo")],
        [InlineKeyboardButton(text="🎬 Видео — 25⭐", callback_data="buy_video")],
        [InlineKeyboardButton(text="👑 Премиум — 50⭐", callback_data="buy_premium")]
    ])
    return kb


# ---------------- BOT INIT ----------------

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# ---------------- HANDLERS ----------------

@dp.message(Command("ref"))
async def ref_cmd(message: types.Message):
    uid = message.from_user.id
    bot_username = (await bot.me()).username
    link = f"https://t.me/{bot_username}?start=ref{uid}"

    await message.answer(
        f"🔗 Ваша реферальная ссылка:\n{link}\n\n"
        f"Приглашайте друзей 😎"
    )


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    args = message.text.split()

    inviter_id = None
    if len(args) > 1 and args[1].startswith("ref"):
        inviter_id = args[1][3:]
        if inviter_id.isdigit():
            inviter_id = int(inviter_id)

    # Відстук про нового юзера
    await bot.send_message(
        GROUP_CHAT_ID,
        f"👋 Новый пользователь: @{message.from_user.username or 'Без ника'} (ID {message.from_user.id})"
    )

    # Реф система
    if inviter_id and inviter_id != message.from_user.id:
        data = load_refs()
        data.setdefault(str(inviter_id), [])

        if str(message.from_user.id) not in data[str(inviter_id)]:
            data[str(inviter_id)].append(str(message.from_user.id))
            save_refs(data)

            await bot.send_message(
                GROUP_CHAT_ID,
                f"👥 Новый реферал!\n"
                f"Пригласил: {inviter_id}\n"
                f"Пользователь: @{message.from_user.username or 'Без ника'} (ID {message.from_user.id})"
            )

    text = (
        "🌶️ Добро пожаловать в *Hot Peppers!* 🔥\n\n"
        "🎯 Доступные коллекции:\n"
        "• Фото — 15⭐\n"
        "• Видео — 25⭐\n"
        "• Премиум — 50⭐"
    )
    await message.answer(text, reply_markup=main_menu(), parse_mode="Markdown")


@dp.callback_query(lambda c: c.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery):
    item = callback.data.split("_")[1]
    amount = {"photo": 15, "video": 25, "premium": 50}[item]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"{item} покупка",
        description=f"Покупка {item} в Hot Peppers 🌶️",
        payload=f"buy_{item}",
        provider_token="",  # XTR Stars — токен пустий
        currency="XTR",
        prices=[LabeledPrice(label=item, amount=amount)],
    )


@dp.pre_checkout_query()
async def pre_checkout(pre: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre.id, ok=True)


@dp.message(lambda m: m.successful_payment)
async def successful_payment(message: types.Message):
    await message.answer("🔥 Оплата успешна! Контент отправится позже.")

    await bot.send_message(
        GROUP_CHAT_ID,
        f"💰 Оплата!\nПользователь: @{message.from_user.username or 'Без ника'}"
    )


# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
