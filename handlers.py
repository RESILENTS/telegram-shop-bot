from asyncio import sleep
from states import NewItem
from database import Item, User
from aiogram import types
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery)
import database
import re
from load_all import dp, bot
from config import channel, admin_group

db = database.DBCommands()

markup = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="🛒 Купить", callback_data="buy"),
            InlineKeyboardButton(text="💰 Продать", callback_data="sales_1")
        ],
        [
            InlineKeyboardButton(text="📃 Инструкция", callback_data="instruction"),
            InlineKeyboardButton(text="❗ Правила", callback_data="regulations")
        ],
        [
            InlineKeyboardButton(text="🔍 Легитчек", callback_data="legitcheck"),
            InlineKeyboardButton(text="💯 Гарант", callback_data="garant")
        ],
        [
            InlineKeyboardButton(text="✌ Отзывы", callback_data="reviews"),
            InlineKeyboardButton(text="💵 Контакты", callback_data="contacts")
        ]

    ]
)
user_markup = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="🛒 Купить", callback_data="buy"),
            InlineKeyboardButton(text="💰 Продать", callback_data="sales_1")
        ],
        [
            InlineKeyboardButton(text="📃 Инструкция", callback_data="instruction"),
            InlineKeyboardButton(text="❗ Правила", callback_data="regulations")
        ],
        [
            InlineKeyboardButton(text="🔍 Легитчек", callback_data="legitcheck"),
            InlineKeyboardButton(text="💯 Гарант", callback_data="garant")
        ],
        [
            InlineKeyboardButton(text="✌ Отзывы", callback_data="reviews"),
            InlineKeyboardButton(text="💵 Контакты", callback_data="contacts")
        ],
        [InlineKeyboardButton(text="🔐 Мой кабинет", callback_data="cabinet")]
    ]
)

cabinet_markup = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="📈 Мои публикации", callback_data="items_history")
        ],
        [
            InlineKeyboardButton(text="↩ В главное меню", callback_data="home")
        ]
    ]
)
cancel_markup = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="🔙 Шаг назад", callback_data="back_step")
        ],
        [
            InlineKeyboardButton(text="⭕ Отмена", callback_data="cancel")
        ]
    ]
)
next_markup = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="Далее", callback_data="price")
        ]
    ]
)
confirm_photo_markup = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="Продолжить", callback_data="change")
        ]
    ]
)
home_markup = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="↩ В главное меню", callback_data="home")
        ]
    ]
)

__delete__ = CallbackData('delete', 'deal_id')

# /start
@dp.message_handler(CommandStart())
async def start(message: types.Message):
    user = await db.get_user(message.from_user.id)
    if user is not None:
        await bot.send_photo(message.from_user.id,
                             "AgACAgIAAxkBAAMqXqWZKY6e8kC5Zd_sDY99woyxGlAAAmCtMRtUoDFJKMQyAAH3FazfqkyAkS4AAwEAAwIAA3gAA02FAgABGQQ",
                             reply_markup=user_markup)
    else:
        await bot.send_photo(message.from_user.id,
                             "AgACAgIAAxkBAAMqXqWZKY6e8kC5Zd_sDY99woyxGlAAAmCtMRtUoDFJKMQyAAH3FazfqkyAkS4AAwEAAwIAA3gAA02FAgABGQQ",
                             reply_markup=markup)

@dp.callback_query_handler(text_contains="cabinet")
async def cabinet(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.delete()
    username = call.from_user.username
    user_id = call.from_user.id
    approval = await db.count_items(str(user_id), True)
    in_process = await db.count_items(str(user_id), False)
    text = ("Привет, {username}\n"
            "Ваши публикации:\n"
            "Опубликованных: <b>{approval}</b> записей\n"
            "На рассмотрении: <b>{in_process}</b> записей\n").\
        format(approval=approval, in_process=in_process, username=username)
    if approval == 0:
        await call.message.answer(text, reply_markup=home_markup)
    else:
        await call.message.answer(text, reply_markup=cabinet_markup)


# список публикаций
@dp.callback_query_handler(text_contains="items_history")
async def user_deals_history(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=home_markup)
    all_items = await db.show_items(str(call.from_user.id))
    for num, item in enumerate(all_items):
        text = ("<b>id:{deal_id}</b> \t|\t <u>{brand}</u>\n"
                "<b>Название:</b> \t{title}\n"
                "<b>Состояние:</b> \t{status}\n"
                "<b>Размер:</b> \t{size}\n"
                "<b>Город:</b> \t{city}\n"
                "<b>Место:</b> \t{place}\n"
                "<b>Цена:</b> \t<b>{price}</b>\n").format(
            deal_id=item.deal_id,
            brand=item.brand,
            title=item.title,
            status=item.status,
            size=item.size,
            city=item.city,
            place=item.place,
            price=item.price
        )
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(text="Удалить", callback_data=__delete__.new(deal_id=item.deal_id))
                ]
            ]
        )
        await call.message.answer(text, reply_markup=markup)
        await sleep(0.3)


# фильтр коллбеков
@dp.callback_query_handler(__delete__.filter())
async def delete_item(call: CallbackQuery, callback_data: dict):
    await call.message.edit_reply_markup()

    deal_id = callback_data.get('deal_id')
    await db.delete_item(deal_id)
    await delete_message(deal_id)
    text = "<b>Ваша публикация {deal_id} была удалена!</b>\n".format(deal_id=callback_data.get('deal_id'))
    callback_data.clear()
    await call.message.answer(text, reply_markup=home_markup)


@dp.callback_query_handler(text_contains="home")
async def back(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.delete()
    user = await db.get_user(call.from_user.id)
    if user is not None:
        await bot.send_photo(call.from_user.id,
                             "AgACAgIAAxkBAAMqXqWZKY6e8kC5Zd_sDY99woyxGlAAAmCtMRtUoDFJKMQyAAH3FazfqkyAkS4AAwEAAwIAA3gAA02FAgABGQQ",
                             reply_markup=user_markup)
    else:
        await bot.send_photo(call.from_user.id,
                             "AgACAgIAAxkBAAMqXqWZKY6e8kC5Zd_sDY99woyxGlAAAmCtMRtUoDFJKMQyAAH3FazfqkyAkS4AAwEAAwIAA3gAA02FAgABGQQ",
                             reply_markup=markup)


@dp.callback_query_handler(text_contains="buy")
async def buy(call: CallbackQuery):
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Вещи в наличии", url="https://t.me/legitplace_stock")
            ],
            [
                InlineKeyboardButton(text="Торговая площадка", url="https://t.me/legitplacemarket")
            ],
            [
                InlineKeyboardButton(text="Legitplace Instagram", url="https://www.instagram.com/legitplace")
            ],
            [
                InlineKeyboardButton(text="↩ В главное меню", callback_data="home")
            ],
        ]
    )
    await call.message.edit_reply_markup()
    await call.message.delete()
    await call.message.answer(
        "🧢 Вещи в наличии:\n@legitplace_stock\n\n👕 Купить вещи пользователей:\n@legitplacemarket",
        reply_markup=markup)


@dp.callback_query_handler(text_contains="reviews")
async def reviews(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.delete()
    await call.message.answer(
        "✅Отзывы о нас ищите в Instagram highlights.\nhttps://www.instagram.com/stories/highlights/18087466135048198"
        "/\nhttps://www.instagram.com/stories/highlights/18050389591005276/\nhttps://www.instagram.com/stories"
        "/highlights/18014711626004061/\nhttps://www.instagram.com/stories/highlights/17888980393173366/",
        reply_markup=home_markup)


@dp.callback_query_handler(text_contains="contacts")
async def contacts(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.delete()
    await call.message.answer(
        "Если у Вас возникли какие-либо вопросы, Вы можете связаться с нами в Telegram и "
        "Instagram.\n\n📭@timewasteog\n📭@buduvsegdal\n\n📸https://www.instagram.com/legitplace",
        reply_markup=home_markup)


@dp.callback_query_handler(text_contains="instruction")
async def instruction(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.delete()
    await call.message.answer(
        "https://telegra.ph/Rukovodstvo-po-polzovaniyu-i-zagruzke-foto-04-18",
        reply_markup=home_markup)


@dp.callback_query_handler(text_contains="regulations")
async def regulations(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.delete()
    await call.message.answer(
        "https://telegra.ph/Pravila-ploshchadki-04-20",
        reply_markup=home_markup)


@dp.callback_query_handler(text_contains="legitcheck")
async def legitcheck(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.delete()
    await call.message.answer_photo(
        "AgACAgIAAxkBAAMtXqWZbsLUabpfMGcOv2FFAvGg6KQAAmmtMRuIDDFJc6AglAjWY2KjZcsOAAQBAAMCAAN4AAOa4QQAARkE",
        reply_markup=home_markup)


@dp.callback_query_handler(text_contains="garant")
async def garant(call: CallbackQuery):
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="🛡 Написать гаранту", url="https://t.me/legitplace_garant")
            ],
            [
                InlineKeyboardButton(text="↩ В главное меню", callback_data="home")
            ]
        ]
    )
    await call.message.edit_reply_markup()
    await call.message.delete()
    await call.message.answer(
        "💯 Единственный контакт гаранта: @legitplace_garant\n\nПравила проведения сделок читайте в документе ниже.\n"
        "https://telegra.ph/Garant-servis-04-21",

        reply_markup=markup)


@dp.callback_query_handler(text_contains="cancel", state=NewItem)
async def cancel(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.delete()
    await state.reset_state()
    await call.message.answer("Вы отменили создание товара", reply_markup=home_markup)


@dp.callback_query_handler(text_contains="back_step", state=NewItem)
async def back_step(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    current_state = await state.get_state()
    if current_state == "NewItem:Brand":
        await bot.delete_message(call.message.chat.id, call.message.message_id)  # рабочий костыль
        await call.message.answer("<b>Шаг 1 из 8</b>\nВведите полное название вещи", reply_markup=cancel_markup)
        await NewItem.Title.set()

    elif current_state == "NewItem:Status":
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await call.message.answer("<b>Шаг 2 из 8</b>\nВведите бренд вещи с хештегом\n<i>Пример:#palace</i>",
                                  reply_markup=cancel_markup)
        await NewItem.Status.set()

    elif current_state == "NewItem:Size":
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await call.message.answer("<b>Шаг 3 из 8</b>\nВведите состояние вещи от 1 до 10 (~9/10) или Новая вещь",
                                  reply_markup=cancel_markup)
        await NewItem.Status.set()

    elif current_state == "NewItem:City":
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await call.message.answer("<b>Шаг 4 из 8</b>\nВведите размер вещи от XXS до XXL", reply_markup=cancel_markup)
        await NewItem.Size.set()

    elif current_state == "NewItem:Place":
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await call.message.answer("<b>Шаг 5 из 8</b>\nВведите город, в котором находится вещь",
                                  reply_markup=cancel_markup)
        await NewItem.City.set()

    elif current_state == "NewItem:Media":
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await call.message.answer("<b>Шаг 6 из 8</b>\nЛичная встреча (где?)/ почта (какая?)",
                                  reply_markup=cancel_markup)
        await NewItem.Place.set()

    elif current_state == "NewItem:Price":
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await call.message.answer(
            "<b>Шаг 7 из 8</b>\nПри помощи скрепки 📎 загрузите более <b>2</b> подробных фотографий",
            reply_markup=cancel_markup)
        await NewItem.Media.set()

    elif current_state == "NewItem:Confirm":
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await call.message.answer("<b>Шаг 8 из 8</b>\nУкажите цену вашего товара", reply_markup=cancel_markup)
        await NewItem.Price.set()


@dp.callback_query_handler(text_contains="sales_1")
async def insctruction(call: CallbackQuery):
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="✏ Начать публикацию", callback_data="sell")
            ],
            [
                InlineKeyboardButton(text="↩ В главное меню", callback_data="home")
            ]
        ]
    )
    await call.message.edit_reply_markup()
    await call.message.delete()
    await bot.send_photo(call.message.chat.id,
                             "AgACAgIAAxkBAAOLXqWePVAoJMYx6-75z_tJWbGqLu8AAmWtMRtUoDFJrSZ_Fw-I87WtX8sOAAQBAAMCAAN4AAPG4QQAARkE",
                             reply_markup=markup)


@dp.callback_query_handler(text_contains="sell")
async def add_new_item(call: CallbackQuery):
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⭕ Отмена", callback_data="cancel")
            ]
        ]
    )
    await call.message.edit_reply_markup()
    if call.from_user.username is None:
        await call.message.answer("Эта функция недоступна для вашего аккаунта.\n"
                                  "Введите имя пользователя в настройках Telegram.", reply_markup=home_markup)
        return
    await call.message.answer("<b>Шаг 1 из 8</b>\nВведите полное название вещи", reply_markup=markup)
    await NewItem.Title.set()


# 1 Хенлдер названия
@dp.message_handler(state=NewItem.Title)
async def enter_name(message: types.Message, state: FSMContext):
    title = message.text
    item = Item()
    item.title = title

    await message.answer("<b>Шаг 2 из 8</b>\nВведите бренд вещи с хештегом\n<i>Пример:#palace</i>",
                         reply_markup=cancel_markup)
    await NewItem.Brand.set()
    await state.update_data(item=item)


# 2 Хенлдер бренда
@dp.message_handler(state=NewItem.Brand)
async def enter_brand(message: types.Message, state: FSMContext):
    brand = message.text
    if brand.startswith('#') is False:
        brand = ('#' + brand)

    data = await state.get_data()
    item: Item = data.get("item")
    item.brand = brand.lower()

    await message.answer("<b>Шаг 3 из 8</b>\nВведите состояние вещи от 1 до 10 (~9/10) "
                         "или Новая вещь", reply_markup=cancel_markup)
    await NewItem.Status.set()
    await state.update_data(item=item)


# 3 Хенлдер состояния
@dp.message_handler(state=NewItem.Status)
async def enter_status(message: types.Message, state: FSMContext):
    status = message.text
    data = await state.get_data()
    item: Item = data.get("item")
    item.status = status

    await message.answer("<b>Шаг 4 из 8</b>\nВведите размер вещи от XXS до XXL", reply_markup=cancel_markup)
    await NewItem.Size.set()
    await state.update_data(item=item)


# 4 Хенлдер размера
@dp.message_handler(state=NewItem.Size)
async def enter_size(message: types.Message, state: FSMContext):
    size = message.text
    data = await state.get_data()
    item: Item = data.get("item")
    item.size = size

    await message.answer("<b>Шаг 5 из 8</b>\nВведите город, в котором находится вещь", reply_markup=cancel_markup)
    await NewItem.City.set()
    await state.update_data(item=item)


# 5 Хенлдер города
@dp.message_handler(state=NewItem.City)
async def enter_city(message: types.Message, state: FSMContext):
    city = message.text
    data = await state.get_data()
    item: Item = data.get("item")
    item.city = city

    await message.answer("<b>Шаг 6 из 8</b>\nЛичная встреча (где?)/ почта (какая?)", reply_markup=cancel_markup)
    await NewItem.Place.set()
    await state.update_data(item=item)


# 6 Хенлдер места встречи
@dp.message_handler(state=NewItem.Place)
async def enter_place(message: types.Message, state: FSMContext):
    place = message.text
    data = await state.get_data()
    item: Item = data.get("item")
    item.place = place

    await message.answer("<b>Шаг 7 из 8</b>\nПри помощи скрепки 📎 загрузите более <b>2</b> подробных фотографий",
                         reply_markup=cancel_markup)
    await NewItem.Media.set()
    await state.update_data(item=item)


@dp.message_handler(state=NewItem.Media, content_types=types.ContentType.DOCUMENT)
async def print_error(message: types.Message):
    chat_id = message.from_user.id
    await bot.send_message(chat_id, "Ошибка, Вы прикрепили документ.")


# 7 Хенлдер фото
@dp.message_handler(state=NewItem.Media, content_types=types.ContentType.PHOTO)
async def enter_media(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    media_id = message.media_group_id
    data = await state.get_data()
    item: Item = data.get("item")
    if media_id is not None:
        item.media = media_id
        await state.update_data(item=item)

    await db.add_photo(media_id, photo_id)
    total_photo = 0
    total_photo = await db.count_photo_by_media_id(media_id)  # подсчет кол-ва фото
    chat_id = message.from_user.id
    if total_photo >= 2:
        msg = await bot.send_message(chat_id,
                                     "Вы прикрепили <b>{total_photo}</b> фото. Для продолжения нажмите кнопку ниже".
                                     format(total_photo=total_photo), reply_markup=confirm_photo_markup)
        await bot.edit_message_text("temp", chat_id, msg.message_id - 1)
        await bot.delete_message(msg.chat.id, msg.message_id - 1)  # рабочий костыль
        await NewItem.Confirm.set()
    else:
        msg = await bot.send_message(chat_id, "Прикрепить как минимум <b>2</b> фото.")
        await bot.edit_message_text("temp", chat_id, msg.message_id - 1)
        await bot.delete_message(msg.chat.id, msg.message_id - 1)  # рабочий костыль


# 8 Хенлдер цены
@dp.message_handler(state=NewItem.Price)
async def get_price(message: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="✅ Отправить на рассмотрение", callback_data="confirm")],
            [InlineKeyboardButton(text="⭕ Отмена", callback_data="cancel")],
        ]
    )

    data = await state.get_data()
    item: Item = data.get("item")
    price = message.text
    if price.isdigit():
        await message.answer("Неверное значение, укажите валюту <i>(USD, UAH, EUR)</i>\n"
                             "<b>Шаг 7 из 7</b>\nУкажите цену и валюту вашего товара, <i>пример:666 USD</i>")
        return
    item.price = price
    item.deal_id = str(message.message_id)
    username = message.from_user.username
    await state.update_data(item=item)
    await message.answer_media_group(await create_media(state, username, None, message))
    await message.answer("Готово!\n", reply_markup=markup)
    await NewItem.Confirm.set()


@dp.callback_query_handler(text_contains="change", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()

    await call.message.answer("<b>Шаг 8 из 8</b>\nУкажите цену и валюту вашего товара")
    await NewItem.Price.set()


@dp.callback_query_handler(text_contains="confirm", state=NewItem.Confirm)
async def confirm(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    username = call.from_user.username
    user_id = call.from_user.id

    await db.add_new_user()

    data = await state.get_data()
    item: Item = data.get("item")
    item.user_id = str(user_id)
    await state.update_data(item=item)
    # await call.message.answer_media_group(await create_media(state, username, call, None))
    await call.bot.send_media_group(admin_group, await create_media(state, username, call, None))
    await call.message.answer("✅Ваше предложение отправлено на рассмотрение!\n"
                              "<b>После успешной продажи зайдите в «Мой кабинет» и "
                              "удалите публикацию. Давайте поддерживать чистоту сообщества вместе :)</b>",
                              reply_markup=home_markup)
    await state.reset_state()


# храним все сообщения канала в БД
@dp.channel_post_handler(content_types=["photo", "file", "media"])
async def message_handler(msg: Message):
    media_id = msg.media_group_id
    deal_id = None
    try:
        deal_id = re.search('id:[0-9]+', msg.caption)
        deal_id = deal_id[0].strip('id:')
        await db.save_message(msg.message_id, str(media_id), deal_id)
        await db.approve_item(deal_id)
        return
    except Exception:
        pass
    await db.save_message(msg.message_id, str(media_id), deal_id)


async def delete_message(deal_id):
    messages_list = await db.get_message_id(deal_id)
    for message_id in messages_list:
        await bot.delete_message(channel, str(message_id).strip('(\',)'))
        await db.delete_message(deal_id)


async def create_media(state: FSMContext, username, call: CallbackQuery = None, msg: Message = None):
    data = await state.get_data()
    item: Item = data.get("item")
    media_id = item.media
    caption = ""
    if call:
        caption = """
🗝 <i>id:{id}  |  {brand}</i>
▪ Название: {title}
▫ Состояние: {status}
▪ Размер: {size}
▫ Цена: <b>{price}</b>
▪ Город: {city}
▫ Отправка: {place}
📭 Контакты: @{username}
➖➖➖🔥🔥🔥➖➖➖
""".format(
            id=item.deal_id,
            title=item.title,
            brand=item.brand,
            status=item.status,
            size=item.size,
            city=item.city,
            place=item.place,
            price=item.price,
            username=username
        )
        await item.create()
    elif msg:
        caption = """
🗝 <i>id:{id}  |  {brand}</i> 
▪ Название: {title}
▫ Состояние: {status}
▪ Размер: {size}
▫ Цена: <b>{price}</b>
▫ Город: {city}
▪ Отправка: {place}
📭 Контакты: @{username}
➖➖➖🔥🔥🔥➖➖➖
""".format(
            id=item.deal_id,
            title=item.title,
            brand=item.brand,
            status=item.status,
            size=item.size,
            city=item.city,
            place=item.place,
            price=item.price,
            username=username
        )
    # Create media group
    media = types.MediaGroup()

    images_list = await db.get_photo_by_media_id(media_id)
    images_dict = {k: images_list[k] for k in range(0, len(images_list))}

    for key, value in images_dict.items():
        if key == 0:
            media.attach_photo(str(value).strip('(\',)'), caption=caption)
        else:
            media.attach_photo(str(value).strip('(\',)')),

    # Done! Send media group
    return media


# chat_id = msg.from_user.id
# await bot.send_message(chat_id, format_dict(msg))
def format_dict(object):
    return format(object) \
        .replace(",", ",\n") \
        .replace("'", "") \
        .replace(
        "{",
        "{\n") \
        .replace(
        "}", "\n}") \
        .replace("[\n", "") \
        .replace("]", "\n]")
