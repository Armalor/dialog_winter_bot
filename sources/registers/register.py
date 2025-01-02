from abc import ABC, abstractmethod
from typing import Optional, Type
from telebot import TeleBot
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
    CallbackQuery,
    Message,
)
from telebot_calendar import CallbackData

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from models import RolesEnum
# ~Локальный импорт


class RegisterNotFoundException(Exception):
    pass


register_callback = CallbackData("register", "role", "step")


class Register(ABC):

    role: Optional[RolesEnum] = None

    title = None

    def __init__(self, bot: TeleBot, initial_message: Message):
        self.register_callback = register_callback
        self.bot = bot
        self.initial_message = initial_message

    @property
    def user_id(self):
        """
        НЕТ, ЭТО НЕ ОШИБКА!
        Идентификатор пользователя (при общении с ботом напрямую, не через группу) это message.chat.id.
        """
        return self.initial_message.chat.id

    @property
    def chat_id(self):
        return self.initial_message.chat.id

    @property
    def message_id(self):
        return self.initial_message.id

    @classmethod
    def factory(cls, role: RolesEnum, bot: TeleBot, initial_message: Message) -> 'Register':

        classes: dict[str, Type[cls]] = {c.role: c for c in cls.__subclasses__()}
        class_ = classes.get(role, None)
        if class_ is not None:
            return class_(bot=bot, initial_message=initial_message)

        raise RegisterNotFoundException

    @abstractmethod
    def get_steps(self) -> InlineKeyboardMarkup:
        pass

    @property
    def finished(self) -> bool:
        return False

    def step_close(self):
        self.bot.delete_message(
            chat_id=self.chat_id,
            message_id=self.message_id,
        )
