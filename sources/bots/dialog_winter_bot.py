import time
import traceback
import logging.config
from logging import Logger
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, CallbackQuery
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
# ~Локальный импорт


class DialogWinterBot(ReporterBot):

    def __init__(self, _logger: Logger = None) -> None:
        super().__init__(_logger)

        self.register_callback = CallbackData("register", "role")

        @self.bot.message_handler(commands=['start'])
        def _(message): self._start(message)

        @self.bot.callback_query_handler(func=lambda c: c.data and c.data.startswith(self.register_callback.prefix))
        def _(callback_query): self._callback_register(callback_query)

    def _start(self, message):

        self.bot.send_message(
            message.chat.id, text="Регистрация",
            reply_markup=self.__get_register_keyboard()
        )

    def _callback_register(self, call: CallbackQuery):
        register, role = call.data.split(self.register_callback.sep)
        print(register, role)

        chat_id = call.message.chat_id
        message_id = call.message.message_id
        text = call.message.text

        self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=self.__get_register_keyboard(role=role)
        )

    def __get_register_keyboard(self, role=None):

        inline_kb = InlineKeyboardMarkup(row_width=1)

        inline_kb.add(
            InlineKeyboardButton(
                'Регистрация участника' + ' ✅' if role == 'student' else '',
                callback_data=self.register_callback.new('student')
            ),
            InlineKeyboardButton(
                'Зарегистрировать друга' + ' ✅' if role == 'friend' else '',
                callback_data=self.register_callback.new('friend')
            ),
            InlineKeyboardButton(
                'Регистрация преподавателя' + ' ✅' if role == 'teacher' else '',
                callback_data=self.register_callback.new('teacher')
            ),
        )

        return inline_kb


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

            reporter.bot.polling(non_stop=True)
        except (ReadTimeout, ReadTimeoutError, ConnectionError, ProtocolError, ConnectionResetError) as error:
            logger.debug(f"Unstable connection: «{str(error).strip()}»; restart.")
        except Exception as error:
            msg = 'Error: «%s»\n%s' % (str(error).strip(), traceback.format_exc())
            logger.error(msg)
        finally:
            attempt += 1
            time.sleep(attempt if attempt <= 30 else 30)
