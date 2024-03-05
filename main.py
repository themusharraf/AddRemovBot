import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters.command import CommandStart, Command
from buttons import user_data, update_num_text, get_keyboard
from aiogram import types

dp = Dispatcher()
TOKEN = ""


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(text="Hi there, I'm a bot")


@dp.message(Command("numbers"))
async def cmd_numbers(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("Raqamni kiriting: 0", reply_markup=get_keyboard())


@dp.callback_query(F.data.startswith("num_"))
async def callbacks_num(callback: types.CallbackQuery):
    user_value = user_data.get(callback.from_user.id, 0)
    action = callback.data.split("_")[1]

    if action == "incr":
        user_data[callback.from_user.id] = user_value + 1
        await update_num_text(callback.message, user_value + 1)
    elif action == "decr":
        user_data[callback.from_user.id] = user_value - 1
        await update_num_text(callback.message, user_value - 1)
    elif action == "finish":
        await callback.message.edit_text(f"Jami: {user_value}")

    await callback.answer()


async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
