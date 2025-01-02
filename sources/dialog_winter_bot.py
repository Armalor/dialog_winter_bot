import time
import traceback
import logging.config
from logging import Logger
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatMemberMember,
    ChatMemberOwner,
    ChatMemberAdministrator,
    CallbackQuery,
    Message,
)
from requests.exceptions import ReadTimeout, ConnectionError
from urllib3.exceptions import ReadTimeoutError, ProtocolError
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
from models import RolesEnum
from registers import Register, register_callback
from admin import Admin, admin_callback
# ~Локальный импорт


class DialogWinterBot(ReporterBot):

    def __init__(self, _logger: Logger = None) -> None:
        super().__init__(_logger)

        @self.bot.message_handler(commands=['start'])
        def _(message): self._start(message)

        @self.bot.callback_query_handler(func=lambda c: c.data and c.data.startswith(register_callback.prefix))
        def _(callback_query): self._callback_register(callback_query)

        @self.bot.callback_query_handler(func=lambda c: c.data and c.data.startswith(admin_callback.prefix))
        def _(callback_query): self._callback_admin(callback_query)

    def is_teacher(self, message):
        # Здесь запрашиваем участника строго конкретного чата:
        chat_member = self.bot.get_chat_member(user_id=message.from_user.id, chat_id=self.chat_id)

        return isinstance(chat_member, ChatMemberMember)

    def is_admin(self, message) -> bool:
        # Для callback'ов сообщение может быть и от бота
        if message.from_user.is_bot:
            user_id = message.chat.id
        else:
            user_id = message.from_user.id

        root = str(user_id) in self.config.telegram.auth and self.config.telegram.auth[str(user_id)]
        if root:
            return True

        chat_member = self.bot.get_chat_member(user_id=user_id, chat_id=self.chat_id)

        return isinstance(chat_member, ChatMemberOwner) or isinstance(chat_member, ChatMemberAdministrator)

    def __get_register_keyboard(self, initial_message=None):

        inline_kb = InlineKeyboardMarkup(row_width=1)

        reg_std = Register.factory(RolesEnum.STUDENT, self.bot, initial_message)

        inline_kb.row(
            InlineKeyboardButton(
                'Зарегистрироваться' + (' ✅' if reg_std.finished else ''),
                callback_data=register_callback.new(RolesEnum.STUDENT, 'get_steps')
            ),
            # InlineKeyboardButton(
            #     'Зарегистрировать друга' ,
            #     callback_data=register_callback.new(RolesEnum.FRIEND, 'get_steps')
            # ),
        )

        if initial_message and self.is_teacher(initial_message):
            reg_tch = Register.factory(RolesEnum.TEACHER, self.bot, initial_message)

            inline_kb.row(
                InlineKeyboardButton(
                    'Регистрация преподавателя' + (' ✅' if reg_tch.finished else ''),
                    callback_data=register_callback.new(RolesEnum.TEACHER, 'get_steps')
                ),
            )

        if initial_message and self.is_admin(initial_message):
            inline_kb.row(
                InlineKeyboardButton('Admin', callback_data=admin_callback.new('action_list', '0'))
            )

        return inline_kb

    def _start(self, message):

        self.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.id,
        )

        self.bot.send_message(
            message.chat.id,
            text="Регистрация / Профиль",
            reply_markup=self.__get_register_keyboard(initial_message=message)
        )

    def _callback_register(self, call: CallbackQuery):
        """
        ВНИМАНИЕ! message.from_user.username / message.from_user.id выдаст «DialogWinterBot» (sic!) и его айдишник
        соответственно — НЕ идентификатор пользователя, ведущего диалог с ботом, т.к. здесь мы редактируем сообщение
        ОТ БОТА! Идентификатор пользователя (при общении с ботом напрямую, не через группу) это message.chat.id.
        """
        register, role, step = call.data.split(register_callback.sep)

        register = Register.factory(role, self.bot, call.message)

        step_method = getattr(register, step, None)
        if step_method and callable(step_method):
            step_method()

    def _callback_admin(self, call: CallbackQuery):

        if not self.is_admin(call.message):
            return

        _, action, modifier = call.data.split(admin_callback.sep)

        admin = Admin(self.bot, call.message)

        action_method = getattr(admin, action, None)

        if action_method and callable(action_method):
            action_method(modifier)


if __name__ == '__main__':
    config = Config.get_instance().config

    logging.config.dictConfig(config.logs)
    logger = logging.getLogger('main')

    reporter = DialogWinterBot(logger)
    attempt = 0

    while True:
        try:
            if attempt == 0:
                msg = f'Start polling {reporter.__class__.__name__}'
            else:
                msg = f'Restart polling {reporter.__class__.__name__}, attempt {attempt}'
            logger.debug(msg)

            reporter.bot.polling(non_stop=False)
        except (ReadTimeout, ReadTimeoutError, ConnectionError, ProtocolError, ConnectionResetError) as error:
            logger.debug(f"Unstable connection: «{str(error).strip()}»; restart.")
        except Exception as error:
            msg = 'Error: «%s»\n%s' % (str(error).strip(), traceback.format_exc())
            logger.error(msg)
        finally:
            attempt += 1
            time.sleep(attempt if attempt <= 30 else 30)
