from abc import ABC, abstractmethod
from typing import Optional, Type
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

    def __init__(self):
        self.register_callback = register_callback

    @classmethod
    def factory(cls, role: RolesEnum) -> 'Register':

        classes: dict[str, Type[cls]] = {c.role: c for c in cls.__subclasses__()}
        class_ = classes.get(role, None)
        if class_ is not None:
            return class_()

        raise RegisterNotFoundException

    @abstractmethod
    def get_steps(self) -> InlineKeyboardMarkup:
        pass
