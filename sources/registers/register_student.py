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

        student = self.get(id=self.user_id, friend_idx=0)

        tail_n = student.name or '❓'
        tail_s = student.school or '❓'
        tail_c = student.cls or '❓'

        inline_kb.add(
            InlineKeyboardButton(f'ФИО: {tail_n}', callback_data=self.register_callback.new(self.role, 'step_name')),
            InlineKeyboardButton(f'Школа: {tail_s}', callback_data=self.register_callback.new(self.role, 'step_school')),
            InlineKeyboardButton(f'Класс: {tail_c}', callback_data=self.register_callback.new(self.role, 'step_class')),
        )

        cnt = 0
        if student.name:
            cnt += 1
        if student.school:
            cnt += 1
        if student.cls:
            cnt += 1

        bra = '<b>' if cnt == 3 else ''
        ket = ', готово!</b>' if cnt == 3 else ''

        self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=f'{self.title}: {bra}{cnt} из 3{ket}',
            reply_markup=inline_kb
        )

        return inline_kb

    def step_name(self, message: Message = None, init_message: Message = None):
        """
        message — это то, что написал пользователь в ответ на запрос фамилии.
        init_message — это сам запрос фамилии, его тоже удаляем.
        """

        if init_message is None:

            init_message = self.bot.send_message(
                chat_id=self.chat_id,
                text="Введите свою <b>фамилию</b> и <b>имя</b>:"
            )

            self.bot.register_next_step_handler(init_message, self.step_name, init_message)

        else:

            student = self.get(id=self.user_id, friend_idx=0)
            student.name = message.text
            student.store()

            self.bot.delete_message(
                chat_id=self.chat_id,
                message_id=message.id,
            )

            self.bot.delete_message(
                chat_id=self.chat_id,
                message_id=init_message.id,
            )

            self.get_steps()

    def step_school(self, message: Message = None, init_message: Message = None):

        if init_message is None:

            replay_kb = ReplyKeyboardMarkup(one_time_keyboard=True)
            for r in range(0, 15, 3):
                replay_kb.row(*[str(k) for k in range(r+1, r+4)])

            sc_list = [
                'Нужен только номер:',
                '1–11 — школы Дубны с первой по одиннадцатую;',
                '12 — лицей «Дубна»;',
                '13 — лицей Кадышевского;',
                '14 — Юна;',
                '15 — любая другая.',
            ]
            sc = '\n'.join(sc_list)
            init_message = self.bot.send_message(
                chat_id=self.chat_id,
                text=f"Укажите школу (просто ткните в кнопку). {sc}",
                reply_markup=replay_kb
            )

            self.bot.register_next_step_handler(init_message, self.step_school, init_message)
        else:

            student = self.get(id=self.user_id, friend_idx=0)

            suffixes = {
                '12': '(лицей «Дубна»)',
                '13': '(лицей Кадышевского)',
                '14': '(Юна)',
                '15': '(другая)',
            }

            student.school = message.text

            if student.school in suffixes:
                student.school += f' {suffixes.get(student.school)}'

            student.store()

            self.bot.delete_message(
                chat_id=self.chat_id,
                message_id=message.id,
            )

            self.bot.delete_message(
                chat_id=self.chat_id,
                message_id=init_message.id,
            )

            self.get_steps()

    def step_class(self, message: Message = None, init_message: Message = None):
        if init_message is None:

            replay_kb = ReplyKeyboardMarkup(one_time_keyboard=True)
            replay_kb.row('меньше 6')
            replay_kb.row('6', '7')
            replay_kb.row('8', '9')
            replay_kb.row('10', '11')
            replay_kb.row('больше 11')

            init_message = self.bot.send_message(
                chat_id=self.chat_id,
                text=f"Укажите класс (просто ткните в кнопку).",
                reply_markup=replay_kb
            )

            self.bot.register_next_step_handler(init_message, self.step_class, init_message)
        else:

            student = self.get(id=self.user_id, friend_idx=0)
            student.cls = message.text
            student.store()

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
        return cls.students

    @classmethod
    def get(cls, id: int, friend_idx: int = 0) -> StudentModel:
        student_list = cls.students.setdefault(id, [])

        try:
            student = student_list[friend_idx].load()
        except IndexError:
            student = StudentModel(id=id, friend_idx=friend_idx).load()
            student_list.append(student)

        return student


if __name__ == '__main__':
    r = RegisterStudent(bot=None, initial_message=None)

    students = r.load()

    print(students)
