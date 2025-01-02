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
from pprint import pprint

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent
sys.path.append(__root__.__str__())
from config import Config
from bots.reporter import ReporterBot
from connector import DBConnector
# ~Локальный импорт


admin_callback = CallbackData("admin", "action", "modifier")


class Admin:

    CURRENT_STAGE = 0

    title = 'Администрирование'

    def __init__(self, bot: TeleBot, initial_message: Message):
        self.callback = admin_callback
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

    def action_list(self, modifier):
        inline_kb = InlineKeyboardMarkup(row_width=1)

        if self.CURRENT_STAGE > 0:
            inline_kb.add(
                InlineKeyboardButton(
                    f'Отправить сигнал «минута до конца {self.CURRENT_STAGE} этапа»',
                    callback_data=self.callback.new('signal_minute', '1')
                )
            )

        inline_kb.add(
            InlineKeyboardButton(f'Начать {self.CURRENT_STAGE+1} этап!', callback_data=self.callback.new('commit_stage', str(self.CURRENT_STAGE+1))),
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

    def commit_stage(self, stage):
        inline_kb = InlineKeyboardMarkup(row_width=1)

        inline_kb.add(
            InlineKeyboardButton(f'Подтверждаю начало {stage} этапа', callback_data=self.callback.new('start_stage', stage)),
            InlineKeyboardButton(f'⬅', callback_data=self.callback.new('action_list', '0')),
        )

        self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=f'<b>{self.title}</b>',
            reply_markup=inline_kb
        )

    def start_stage(self, stage):
        inline_kb = InlineKeyboardMarkup(row_width=1)
        self.bot.send_message(
            chat_id=self.chat_id,
            text=f"НАЧИНАЕМ {stage} ЭТАП"
        )

        Admin.CURRENT_STAGE = 1
