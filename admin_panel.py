from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import admin_id
from load_all import dp, bot
from states import NewItem, Mailing
from database import Item, User, DBCommands

db = DBCommands()

markup = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="Рассылка", callback_data="mailing")
        ]
    ]
)

cancel_markup = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="⭕ Отмена", callback_data="cancel")
        ]
    ]
)

@dp.message_handler(user_id=admin_id, commands=["admin"])
async def admin_menu(message: types.Message):
    await message.answer("Хеллоу, Админ", reply_markup=markup)


# Фича для рассылки по юзерам
@dp.callback_query_handler(user_id=admin_id, text_contains="mailing")
async def mailing_menu(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await Mailing.Text.set()
    users = await db.count_users()
    await call.message.answer("Рассылку получат <b>{total_users}</b> юзеров\n"
                              "Введите текст рассылки".format(total_users=users),
                              reply_markup=cancel_markup)


@dp.message_handler(user_id=admin_id, state=Mailing.Text)
async def mailing_start(msg: types.Message, state: FSMContext):
    text = msg.text
    await state.reset_state()

    users = await User.query.gino.all()
    for user in users:
        try:
            await bot.send_message(user.user_id, text)
            await sleep(0.3)
        except Exception:
            pass
    await msg.answer("Рассылка выполнена.")


@dp.callback_query_handler(user_id=admin_id, state=Mailing.Text)
async def cancel_mailing(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    await call.message.edit_reply_markup()
    await call.message.answer("Рассылка отменена, /start - начало")


