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
from models import RolesEnum, StudentModel, StudentsModel
from registers.register import Register
# ~Локальный импорт


class RegisterStudent(Register):

    role: Optional[RolesEnum] = RolesEnum.STUDENT

    title = 'Профиль участника'

    students: StudentsModel = StudentsModel()

    def get_steps(self):
        inline_kb = InlineKeyboardMarkup(row_width=1)

        tail_n = '❓'
        # if self.initial_message.chat.last_name and self.initial_message.chat.first_name:
        #     tail_n = f'{self.initial_message.chat.last_name} {self.initial_message.chat.first_name}'

        tail_s = '❓'
        tail_c = '❓'

        inline_kb.add(
            InlineKeyboardButton(f'ФИО: {tail_n}', callback_data=self.register_callback.new(self.role, 'step_name')),
            InlineKeyboardButton(f'Школа: {tail_s}', callback_data=self.register_callback.new(self.role, 'step_school')),
            InlineKeyboardButton(f'Класс: {tail_c}', callback_data=self.register_callback.new(self.role, 'step_class')),
        )

        self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=self.title,
            reply_markup=inline_kb
        )

        return inline_kb

    def step_name(self):
        print('step_name')

    def step_school(self):
        print('step_school')

    def step_class(self):
        print('step_class')

    @classmethod
    def load(cls) -> StudentsModel:
        return cls.students

    @classmethod
    def get(cls, id: int, friend_idx: int = 0) -> StudentModel:
        student_list = cls.students.setdefault(id, [])

        try:
            student = student_list[friend_idx]
        except IndexError:
            student = StudentModel(id=id, friend_idx=friend_idx)
            student_list.append(student)

        return student

    # @classmethod
    # def set(cls, student: StudentModel):
    #
    #     student_list = cls.students.setdefault(student.id, [])
    #     try:
    #         student_list[student.friend_idx] = student
    #     except IndexError:
    #         student_list.append(student)


if __name__ == '__main__':
    r = RegisterStudent(initial_message=None)

    students = r.load()

    print(students)
