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
from telebot_calendar import CallbackData

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from models import RolesEnum
from .register import Register
# ~Локальный импорт


class RegisterTeacher(Register):

    role: Optional[RolesEnum] = RolesEnum.TEACHER
    title = 'Профиль препода'

    def get_steps(self):
        inline_kb = InlineKeyboardMarkup(row_width=1)

        student = self.get(id=self.user_id, friend_idx=0)

        tail_sn = student.surname or '❓'
        tail_n = student.name or '❓'

        inline_kb.add(
            InlineKeyboardButton('Контрольный пункт:', callback_data=self.register_callback.new(self.role, 'step_checkpoint')),
            InlineKeyboardButton('Тайминг:', callback_data=self.register_callback.new(self.role, 'step_timing')),
            InlineKeyboardButton(f'❌', callback_data=self.register_callback.new(self.role, 'step_close')),
        )

        self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=f'{self.title}',
            reply_markup=inline_kb
        )
