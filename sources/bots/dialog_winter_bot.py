import time
import traceback
import logging.config
from logging import Logger
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, CallbackQuery
from requests.exceptions import ReadTimeout, ConnectionError
from urllib3.exceptions import ReadTimeoutError, ProtocolError
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

        self.runner_dir = __root__ / 'parsers'

        self.session_pid: int = -1

        self.loading_document = False

        @self.bot.message_handler(commands=['start'])
        def _(message): self._start(message)

    def _start(self, message):
        self.bot.send_message(
            message.chat.id,
            f"Привет! chat_id = {message.chat.id}; user_id = {message.from_user.id}; bot = {self.__class__.__name__}"
        )
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn1 = KeyboardButton("Как меня зовут?")
        back = KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, back)
        self.bot.send_message(message.chat.id, text="Задай мне вопрос", reply_markup=markup)


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
