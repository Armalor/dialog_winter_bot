from typing import Optional
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
    CallbackQuery,
    Message,
)

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from models import RolesEnum
from .register import Register
# ~Локальный импорт


class RegisterStudent(Register):

    role: Optional[RolesEnum] = RolesEnum.STUDENT

    title = 'Профиль участника'

    def get_steps(self):
        inline_kb = InlineKeyboardMarkup(row_width=1)

        tail = '❓'

        inline_kb.add(
            InlineKeyboardButton(f'ФИО: {tail}', callback_data=self.register_callback.new(self.role, 'step_name')),
            InlineKeyboardButton(f'Школа: {tail}', callback_data=self.register_callback.new(self.role, 'step_school')),
            InlineKeyboardButton(f'Класс: {tail}', callback_data=self.register_callback.new(self.role, 'step_class')),
        )

        return inline_kb

    def step_name(self):
        """ФИО"""
        ...

    def step_school(self):
        """Школа"""
        ...

    def step_class(self):
        """Класс"""
        ...
