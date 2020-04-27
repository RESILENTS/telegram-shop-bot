from aiogram import types, Bot
from gino import Gino
from sqlalchemy import (Column, Integer, BigInteger, String,
                        Sequence, TIMESTAMP, Boolean, JSON, func, and_)
from sqlalchemy import sql, select, update

from config import db_pass, db_user, host

db = Gino()


# Документация
# http://gino.fantix.pro/en/latest/tutorials/tutorial.html

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger)
    username = Column(String(50))
    query: sql.Select

    def __repr__(self):
        return "<User(id='{}', username='{}')>".format(
            self.id, self.username)


class Item(db.Model):
    __tablename__ = 'items'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(String(100))
    deal_id = Column(String(50))
    approve = Column(Boolean, default=False)
    title = Column(String(50))
    brand = Column(String(100))
    status = Column(String(20))
    size = Column(String(20))
    city = Column(String(30))
    place = Column(String(60))
    media = Column(String(250))
    price = Column(String(20))

    def __repr__(self):
        return "<Item(id='{}', user_id='{}, deal_id='{}', title='{}', brand='{}',status='{}', size='{}', city='{}', place='{}', media'{}', price='{}')>".format(
            self.id, self.user_id, self.deal_id, self.title, self.brand, self.status, self.size, self.city, self.place,
            self.media, self.price)


class Photo(db.Model):
    __tablename__ = 'photos'
    query: sql.Select

    id = Column(Integer, Sequence('photo_id_seq'), primary_key=True)
    media_id = Column(String(250))
    photo_id = Column(String(250))

    def __repr__(self):
        return "<Photo(id='{}', media_id='{}', photo_id'{}'>".format(self.id, self.media_id, self.photo_id)


class Message(db.Model):
    __tablename__ = 'messages'
    query: sql.Select

    id = Column(Integer, Sequence('message_id_seq'), primary_key=True)
    message_id = Column(BigInteger)
    media_group_id = Column(String(250))
    deal_id = Column(String(250))

    def __repr__(self):
        return "<Message(id='{}', message_id='{}', media_group_id'{}', deal_id'{}'>".format(
            self.id, self.message_id, self.media_group_id, self.deal_id)


class DBCommands:

    async def get_user(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    async def add_new_user(self):
        user = types.User.get_current()
        old_user = await self.get_user(user.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.user_id = user.id
        new_user.username = "@" + user.username
        await new_user.create()
        return new_user

    async def count_items(self, user_id, approve) -> int:
        return await (db.select([db.func.count()]).where(and_(Item.user_id == user_id, Item.approve == approve))).gino.scalar()

    async def approve_item(self, deal_id):
        await (update(Item).where(Item.deal_id == deal_id).values(approve=True)).gino.all()
        return True

    async def show_items(self, user_id):
        return await Item.query.where(and_(Item.user_id == user_id, Item.approve == True)).gino.all()

    async def delete_item(self, deal_id):
        await Item.delete.where(Item.deal_id == deal_id).gino.status()

    async def add_photo(self, media_id, photo_id):
        return await Photo.create(media_id=media_id, photo_id=photo_id)

    async def get_photo_by_media_id(self, media_id):
        return await Photo.select('photo_id').where(Photo.media_id == media_id).gino.all()

    async def count_photo_by_media_id(self, media_id) -> int:
        if media_id is not None:
            return await db.select([db.func.count()]).where(Photo.media_id == media_id).gino.scalar()
        else:
            return 0

    async def count_users(self) -> int:
        return await db.func.count(User.id).gino.scalar()

    async def save_message(self, message_id, media_id, deal_id):
        if deal_id is None:
            await Message.create(message_id=message_id, media_group_id=media_id, deal_id=deal_id)
            deal_id = str(await Message.select('deal_id')
                          .where(Message.deal_id is not None and Message.media_group_id == media_id)
                          .gino.first()).strip('(\',)')
            q = (update(Message).where(Message.media_group_id == media_id).
                 values(deal_id=deal_id))
            await q.gino.all()
        else:
            await Message.create(message_id=message_id, media_group_id=media_id, deal_id=deal_id)
        return True

    async def get_message_id(self, deal_id):
        return await Message.select('message_id').where(Message.deal_id == deal_id).gino.all()

    async def delete_message(self, deal_id):
        await Message.delete.where(Message.deal_id == deal_id).gino.status()


async def create_db():
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/gino')

    # Create tables
    # db.gino: GinoSchemaVisitor
    # await db.gino.drop_all()
    await db.gino.create_all()
