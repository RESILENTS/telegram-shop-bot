from aiogram.dispatcher.filters.state import StatesGroup, State


class NewItem(StatesGroup):
    Title = State()
    Brand = State()
    Status = State()
    Size = State()
    City = State()
    Place = State()
    Media = State()
    Price = State()
    Confirm = State()

# class DeleteItem(StatesGroup):


class Mailing(StatesGroup):
    Text = State()
