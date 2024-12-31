import time
import traceback
import logging.config
from logging import Logger
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
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
# ~Локальный импорт


class DialogWinterBot(ReporterBot):

    def __init__(self, _logger: Logger = None) -> None:
        super().__init__(_logger)

        @self.bot.message_handler(commands=['start'])
        def _(message): self._start(message)

        @self.bot.callback_query_handler(func=lambda c: c.data and c.data.startswith(register_callback.prefix))
        def _(callback_query): self._callback_register(callback_query)

    @staticmethod
    def __get_register_keyboard(role=None):

        inline_kb = InlineKeyboardMarkup(row_width=1)

        inline_kb.add(
            InlineKeyboardButton(
                'Зарегистрироваться' + (' ✅' if role == 'student' else ''),
                callback_data=register_callback.new('student', 'get_steps')
            ),
            InlineKeyboardButton(
                'Зарегистрировать друга' + (' ✅' if role == 'friend' else ''),
                callback_data=register_callback.new('friend', 'get_steps')
            ),
            InlineKeyboardButton(
                'Регистрация преподавателя' + (' ✅' if role == 'teacher' else ''),
                callback_data=register_callback.new('teacher', 'get_steps')
            ),
        )

        return inline_kb

    def _start(self, message):

        self.bot.send_message(
            message.chat.id,
            text="Регистрация / Профиль",
            reply_markup=self.__get_register_keyboard()
        )

    def _callback_register(self, call: CallbackQuery):
        register, role, step = call.data.split(register_callback.sep)

        print(register, role, step)

        if 'get_steps' == step:

            chat_id = call.message.chat.id
            message_id = call.message.message_id
            text = call.message.text

            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=self.__get_register_keyboard(role=role)
            )

        self.register_step(call.message, role, step)

    def register_step(self, message: Message, role, step: str):
        """
        ВНИМАНИЕ! message.from_user.username / message.from_user.id выдаст «DialogWinterBot» (sic!) и его айдишник
        соответственно — НЕ идентификатор пользователя, ведущего диалог с ботом, т.к. здесь мы редактируем сообщение
        ОТ БОТА! Идентификатор пользователя (при общении с ботом напрямую, не через группу) это message.chat.id.
        """


        print(message.chat.last_name, message.chat.first_name)

        register = Register.factory(role, self.bot, message)

        step_method = getattr(register, step, None)
        if step_method and callable(step_method):
            step_method()


        # steps = {
        #     0: {
        #         RolesEnum.STUDENT: '<b>Введите ФИО:</b>',
        #         RolesEnum.FRIEND: '<b>Введите ФИО друга:</b>',
        #         RolesEnum.TEACHER: '<b>Введите ФИО:</b>',
        #     }
        # }
        #
        # print(role, step, register)
        # chat_id = message.chat.id
        #
        # self.bot.send_message(
        #     chat_id=chat_id,
        #     text=steps[step][role]
        # )
        #
        # self.bot.register_next_step_handler(message, self.register_step, role, 'surname')


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
            logger.info(msg)

            reporter.bot.polling(non_stop=False)
        except (ReadTimeout, ReadTimeoutError, ConnectionError, ProtocolError, ConnectionResetError) as error:
            logger.debug(f"Unstable connection: «{str(error).strip()}»; restart.")
        except Exception as error:
            msg = 'Error: «%s»\n%s' % (str(error).strip(), traceback.format_exc())
            logger.error(msg)
        finally:
            attempt += 1
            time.sleep(attempt if attempt <= 30 else 30)
