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
import random
from pprint import pprint

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent
sys.path.append(__root__.__str__())
from config import Config
from bots.reporter import ReporterBot
from connector import DBConnector
from utils.allocation import allocation_step, get_checkpoints_from_db, get_students_from_db
from registers import RegisterStudent
from models import TeacherModel
# ~Локальный импорт


admin_callback = CallbackData("admin", "action", "modifier")


class Admin:

    CURRENT_STAGE = 0

    title = 'Администрирование'

    def __init__(self, bot: TeleBot, initial_message: Message):
        self.callback = admin_callback
        self.bot = bot
        self.initial_message = initial_message

        # Определяем текущий этап на случай падения бота:
        students = get_students_from_db()
        if len(students):
            st = students[0]
            Admin.CURRENT_STAGE = len(st.checkpoints)

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

    def action_list(self, modifier):
        inline_kb = InlineKeyboardMarkup(row_width=1)

        if self.CURRENT_STAGE > 0:
            inline_kb.add(
                InlineKeyboardButton(
                    f'Сбросить все в начало',
                    callback_data=self.callback.new('commit_reset', '0')
                )
            )

            inline_kb.add(
                InlineKeyboardButton(
                    f'Отправить сигнал «минута до конца {self.CURRENT_STAGE} этапа»',
                    callback_data=self.callback.new('sigterm', '1')
                )
            )

        inline_kb.add(
            InlineKeyboardButton(
                f'Начать {self.CURRENT_STAGE+1} этап!',
                callback_data=self.callback.new('commit_stage', str(self.CURRENT_STAGE+1))
            ),
            InlineKeyboardButton(f'⬅', callback_data=self.callback.new('close', '0')),
        )

        self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=f'<b>{self.title}</b>',
            reply_markup=inline_kb
        )

    def close(self, modifier):
        self.bot.delete_message(
            chat_id=self.chat_id,
            message_id=self.message_id,
        )

    def commit_reset(self, stage='0'):
        inline_kb = InlineKeyboardMarkup(row_width=1)

        tail_c = ' ✅' if stage == '1' else ''

        inline_kb.add(
            InlineKeyboardButton(f'Подтверждаю сброс в начало' + tail_c,
                                 callback_data=self.callback.new('commit_reset', '1')),
            InlineKeyboardButton(f'⬅', callback_data=self.callback.new('action_list', '0')),
        )

        self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=f'<b>{self.title}</b>',
            reply_markup=inline_kb
        )

        if '1' == stage:
            # Надо почистить
            students = get_students_from_db()
            checkpoints = get_checkpoints_from_db()

            with DBConnector() as cur:
                for s in students:
                    s.checkpoints = []
                    s.save(cur=cur)
                for c in checkpoints:
                    c.students = []
                    c.save(cur=cur)

            self.bot.send_message(
                chat_id=self.chat_id,
                text=f"СБРОС ВСЕХ ЭТАПОВ"
            )

    def commit_stage(self, stage, committed=False):

        inline_kb = InlineKeyboardMarkup(row_width=1)

        tail_c = ' ✅' if committed else ''

        inline_kb.add(
            InlineKeyboardButton(f'Подтверждаю начало {stage} этапа' + tail_c, callback_data=self.callback.new('start_stage', stage)),
            InlineKeyboardButton(f'⬅', callback_data=self.callback.new('action_list', '0')),
        )

        self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=f'<b>{self.title}</b>',
            reply_markup=inline_kb
        )

    def start_stage(self, stage):

        self.commit_stage(stage, True)
        self.bot.send_message(
            chat_id=self.chat_id,
            text=f"НАЧИНАЕМ ЭТАП: {stage}"
        )

        Admin.CURRENT_STAGE = int(stage)

        tick = Admin.CURRENT_STAGE - 1
        print(f'')
        print(f'')
        print(f'############ TICK {tick + 1}')

        students = get_students_from_db()
        checkpoints = get_checkpoints_from_db()
        # print(students, checkpoints)

        if 0 == tick:
            # Надо почистить
            with DBConnector() as cur:
                for s in students:
                    s.checkpoints = []
                    s.save(cur=cur)
                for c in checkpoints:
                    c.students = []
                    c.save(cur=cur)

        students, checkpoints = allocation_step(students, checkpoints, tick)

        total = 0
        for ch in checkpoints:
            print('')
            print(f'{ch.name}: {ch.total}', 'ТУТ ДЕТИ!' if ch.kids else '')
            tick_students = ch.students[-1]
            surnames = list(map(lambda x: x.surname, tick_students))
            print(surnames, len(surnames))

            total += ch.total
        print(f'total: {total / (tick + 1)}')

        with DBConnector() as cur:
            for s in students:  #
                s.save(cur=cur)
                s_ch = s.checkpoints[-1]

                self.bot.send_message(
                    chat_id=s.id,
                    text=f"Участник {s.surname} {s.name}, начался этап #{Admin.CURRENT_STAGE} — немедленно мчи на КП {s_ch}!"
                )

            teachers: list[TeacherModel] = []

            cur.execute('select * from teachers')
            for tch in cur.fetchall():
                teachers.append(TeacherModel.model_validate(tch))

            for c in checkpoints:
                c.save(cur=cur)

                if c.kids:
                    team = ' мелких детей.'
                else:
                    c_students = c.students[-1]
                    suffix = 'a' if 1 == len(c_students) else ''
                    team = f' из {len(c_students)} человек{suffix}:\n'
                    names = [f'{s.name} {s.surname}' for s in c_students]
                    team += ';\n'.join(names)
                    team += '.'

                prefixes = [
                    'яростно',
                    'задорно',
                    'роняя тапки',
                    'свирепо',
                    'изо всех сил',
                    'отчаянно',
                    'угрюмо',
                    'сосредоточенно',
                    'стадом кабанов',
                    'стаей лосей',
                    'на последнем издыхании',
                    'в яростном угаре',
                ]
                for t in teachers:
                    if t.checkpoint == c.name:
                        prefix = random.choice(prefixes)
                        self.bot.send_message(
                            chat_id=t.id,
                            text=f"Препод, {t.name}, вминание! Начался этап #{Admin.CURRENT_STAGE}, "
                                 f"к тебе — КП {c.name} — {prefix} мчит команда {team}"
                        )

                    if t.kids and c.kids:
                        self.bot.send_message(
                            chat_id=t.id,
                            text=f"Препод {t.name} (по мелким), вминание! Начался этап #{Admin.CURRENT_STAGE}, "
                                 f"собирай своих подопечных и стаей кабанчиков с ними на КП <b>{c.name}</b>"
                        )

        # print(students, checkpoints)

    def sigterm(self, stage):
        ...
