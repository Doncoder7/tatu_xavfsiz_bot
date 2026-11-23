from aiogram.filters import BaseFilter
from aiogram.types import Message
import database as db

class IsStaff(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = await db.get_user(message.from_user.id)
        return bool(user and user['role'] == 'staff')

class IsStudent(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = await db.get_user(message.from_user.id)
        return not bool(user and user['role'] == 'staff')
