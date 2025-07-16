from psycopg2.extensions import cursor
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
from pprint import pprint

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from models import RolesEnum, StudentModel, StudentsModel
from registers.register import Register
from connector import DBConnector
# ~Локальный импорт


class RegisterStudent(Register):

    role: Optional[RolesEnum] = RolesEnum.STUDENT

    title = 'Профиль участника'

    students: StudentsModel = StudentsModel()

    @property
    def finished(self) -> bool:
        student = self.get(id=self.user_id, friend_idx=0)

        return all([
            student.surname is not None,
            student.name is not None,
        ])

    def get_steps(self):
        inline_kb = InlineKeyboardMarkup(row_width=1)

        student = self.get(id=self.user_id, friend_idx=0)

        tail_sn = student.surname or '❓'
        tail_n = student.name or '❓'

        inline_kb.add(
            InlineKeyboardButton(f'Фамилия: {tail_sn}', callback_data=self.register_callback.new(self.role, 'step_surname')),
            InlineKeyboardButton(f'Имя: {tail_n}', callback_data=self.register_callback.new(self.role, 'step_name')),
            InlineKeyboardButton(f'⬅', callback_data=self.register_callback.new(self.role, 'step_close')),
        )
        total_cnt = 2
        cnt = 0
        if student.surname:
            cnt += 1
        if student.name:
            cnt += 1

        finished = '\n<b>РЕГИСТРАЦИЯ ЗАВЕРШЕНА, СПАСИБО!</b>' if self.finished else ''

        self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=f'{self.title}: {cnt} из {total_cnt}. {finished}',
            reply_markup=inline_kb
        )

    def step_surname(self, message: Message = None, init_message: Message = None):
        """
        message — это то, что написал пользователь в ответ на запрос фамилии.
        init_message — это сам запрос фамилии, его тоже удаляем.
        """

        if init_message is None:

            init_message = self.bot.send_message(
                chat_id=self.chat_id,
                text="Введите свою <b>фамилию</b>:"
            )

            self.bot.register_next_step_handler(init_message, self.step_surname, init_message)

        else:

            student = self.get(id=self.user_id, friend_idx=0)
            student.surname = message.text
            student.save()

            self.bot.delete_message(
                chat_id=self.chat_id,
                message_id=message.id,
            )

            self.bot.delete_message(
                chat_id=self.chat_id,
                message_id=init_message.id,
            )

            self.get_steps()

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

            student = self.get(id=self.user_id, friend_idx=0)
            student.name = message.text
            student.save()

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
    def load(cls) -> StudentsModel:
        with DBConnector() as cur:
            cur.execute('select * from students')
            for std in cur.fetchall():
                _ = cls.get(id=std['id'], friend_idx=std['friend_idx'], cur=cur)

        return cls.students

    @classmethod
    def get(cls, id: int, friend_idx: int = 0, cur: cursor = None) -> StudentModel:
        student_list = cls.students.setdefault(id, [])

        try:
            student = student_list[friend_idx].load(cur=cur)
        except IndexError:
            student = StudentModel(id=id, friend_idx=friend_idx).load(cur=cur)
            student_list.append(student)

        return student


if __name__ == '__main__':
    r = RegisterStudent(bot=None, initial_message=None)

    students = r.load()

    pprint(students)
