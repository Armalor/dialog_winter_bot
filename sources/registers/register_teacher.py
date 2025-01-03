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
from models import RolesEnum, TeacherModel
from .register import Register
from connector import DBConnector
# ~Локальный импорт


class RegisterTeacher(Register):

    role: Optional[RolesEnum] = RolesEnum.TEACHER
    title = 'Профиль препода'

    TEACHER_KIDS = 'Сопровождаю мелких детей'
    DELETE_CHECKPOINT = 'Нет КП (удалить)'

    teachers: dict[int, TeacherModel] = dict()

    @property
    def finished(self) -> bool:
        teacher = self.get(id=self.user_id)

        return all([
            teacher.name is not None,
            teacher.checkpoint is not None or teacher.kids,
        ])

    def get_steps(self):
        inline_kb = InlineKeyboardMarkup(row_width=1)

        teacher = self.get(id=self.user_id)

        tail_n = teacher.name or '❓'
        tail_c = teacher.checkpoint or '❓'

        if teacher.kids:
            tail_c = self.TEACHER_KIDS

        inline_kb.add(
            InlineKeyboardButton(f'Имя: {tail_n}', callback_data=self.register_callback.new(self.role, 'step_name')),
            InlineKeyboardButton(f'Контрольный пункт: {tail_c}', callback_data=self.register_callback.new(self.role, 'step_checkpoint')),
            # InlineKeyboardButton('Тайминг:', callback_data=self.register_callback.new(self.role, 'step_timing')),
            InlineKeyboardButton(f'⬅', callback_data=self.register_callback.new(self.role, 'step_close')),
        )

        self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=f'{self.title}',
            reply_markup=inline_kb
        )

    def step_name(self, message: Message = None, init_message: Message = None):
        """
        message — это то, что написал пользователь в ответ на запрос фамилии.
        init_message — это сам запрос фамилии, его тоже удаляем.
        """

        if init_message is None:

            init_message = self.bot.send_message(
                chat_id=self.chat_id,
                text="Введите свое <b>имя</b>:"
            )

            self.bot.register_next_step_handler(init_message, self.step_name, init_message)

        else:

            teacher = self.get(id=self.user_id)
            teacher.name = message.text
            teacher.save()

            self.bot.delete_message(
                chat_id=self.chat_id,
                message_id=message.id,
            )

            self.bot.delete_message(
                chat_id=self.chat_id,
                message_id=init_message.id,
            )

            self.get_steps()

    def step_checkpoint(self, message: Message = None, init_message: Message = None):

        if init_message is None:

            replay_kb = ReplyKeyboardMarkup(one_time_keyboard=True)

            replay_kb.row(self.DELETE_CHECKPOINT)
            replay_kb.row(self.TEACHER_KIDS)

            with DBConnector() as cursor:
                cursor.execute('select * from checkpoints order by name')

                for checkpoint in cursor.fetchall():
                    replay_kb.row(checkpoint['name'])

            init_message = self.bot.send_message(
                chat_id=self.chat_id,
                text=f"Укажите КП (просто ткните в кнопку)",
                reply_markup=replay_kb
            )

            self.bot.register_next_step_handler(init_message, self.step_checkpoint, init_message)
        else:

            teacher = self.get(id=self.user_id)

            if self.DELETE_CHECKPOINT == message.text:
                teacher.checkpoint = None
                teacher.kids = False
            elif self.TEACHER_KIDS == message.text:
                teacher.checkpoint = None
                teacher.kids = True
            else:
                teacher.checkpoint = message.text
                teacher.kids = False

            teacher.save()

            self.bot.delete_message(
                chat_id=self.chat_id,
                message_id=message.id,
            )

            self.bot.delete_message(
                chat_id=self.chat_id,
                message_id=init_message.id,
            )

            self.get_steps()


    @classmethod
    def get(cls, id: int) -> TeacherModel:
        teacher = cls.teachers.setdefault(id, TeacherModel(id=id).load())

        return teacher
