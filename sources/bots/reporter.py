from telebot import TeleBot
from telebot.types import ChatMemberOwner, ChatMemberAdministrator
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from logging import Logger
from pprint import pprint

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from config import Config
# ~Локальный импорт


class ReporterBot:

    def __init__(self, _logger: Logger = None):
        self.config = Config().config

        self.logger = _logger

        self.bot = TeleBot(Config().config.telegram.token, parse_mode='HTML')

        self.chat_id = self.config.logs.handlers.telegram.chat_id

        @self.bot.message_handler(commands=['settings'])
        def _(message): self._settings(message)

        @self.bot.message_handler(commands=['auth'])
        @self.authorized
        def _(message): self._auth(message)

    def _settings(self, message):
        self.bot.send_message(
            message.chat.id,
            f"Привет! chat_id = {message.chat.id}; user_id = {message.from_user.id}; bot = {self.__class__.__name__}"
        )

    def _test(self, message):
        inline_btn_1 = InlineKeyboardButton('Первая кнопка!', callback_data='button1')
        inline_kb_full = InlineKeyboardMarkup(row_width=2).add(inline_btn_1)
        inline_kb_full.add(InlineKeyboardButton('Вторая кнопка', callback_data='btn2'))
        inline_btn_3 = InlineKeyboardButton('кнопка 3 с очень длинным текстом', callback_data='btn3')
        inline_btn_4 = InlineKeyboardButton('кнопка 4', callback_data='btn4')
        inline_btn_5 = InlineKeyboardButton('Ханты-мансийский АО', callback_data='btn5')
        inline_kb_full.add(inline_btn_3, inline_btn_4, inline_btn_5)
        inline_kb_full.row(inline_btn_3, inline_btn_4, inline_btn_5)
        inline_kb_full.add(InlineKeyboardButton("query=''", switch_inline_query=''))
        inline_kb_full.add(InlineKeyboardButton("query='qwerty'", switch_inline_query='qwerty'))
        inline_kb_full.add(InlineKeyboardButton("Inline в этом же чате", switch_inline_query_current_chat='wasd'))

        self.bot.send_message(message.chat.id, text="Отправляю все возможные кнопки", reply_markup=inline_kb_full)

    def process_callback_kb1btn1(self, callback_query: CallbackQuery):
        code = callback_query.data[-1]

        if code.isdigit():
            code = int(code)
        if code == 2:
            self.bot.answer_callback_query(callback_query.id, text='Нажата вторая кнопка')
        elif code == 5:
            self.bot.answer_callback_query(
                callback_query.id,
                text='Нажата кнопка с номером 5', show_alert=True)
        else:
            self.bot.answer_callback_query(callback_query.id)

        self.bot.send_message(callback_query.message.chat.id, text=f'Нажата инлайн-кнопка code={code}!')

    def __auth(self, message):
        _id = str(message.from_user.id)
        # Дополнительная проверка: если есть рутовый доступ базовом config.production.json для пользователя 12345678,
        # и мы хотим этот доступ закрыть в одном из подкаталогов, то в нужных местах вставляем "12345678": false в
        # блок telegram.auth.
        root = _id in self.config.telegram.auth and self.config.telegram.auth[_id]
        if root:
            return True

        # Здесь запрашиваем участника строго конкретного чата:
        chat_member = self.bot.get_chat_member(user_id=message.from_user.id, chat_id=self.chat_id)

        return isinstance(chat_member, ChatMemberOwner) or isinstance(chat_member, ChatMemberAdministrator)

    def _auth(self, message):
        try:
            chat_id = message.chat.id
        except AttributeError:
            # Это для CallbackQuery, иначе получаем «AttributeError: 'CallbackQuery' object has no attribute 'chat'»
            chat_id = message.message.chat.id

        # Здесь вызывать self.__auth(message) просто не нужно: если мы до сюда дошли, значит авторизация уже точно
        # пройдена за счет декоратора @authorized
        _id = str(message.from_user.id)

        # Проверяем, что это рутовый юзер:
        root = True
        username = self.config.telegram.auth.get(_id, {}).get('name', False)

        if not username:
            root = False
            username = f"(@{message.from_user.username or '???'}) {message.from_user.first_name or '???'} {message.from_user.last_name or '???'}"

        self.bot.send_message(
            chat_id,
            f"Доступ разрешен: {username}{' (root user)' if root else ''}"
        )

    def authorized(self, fn):
        def wrapper(*args, **kwargs):
            message = args[0]
            try:
                chat_id = message.chat.id
            except AttributeError:
                # Это для CallbackQuery, иначе получаем «AttributeError: 'CallbackQuery' object has no attribute 'chat'»
                chat_id = message.message.chat.id

            if not self.__auth(message):
                self.bot.send_message(
                    chat_id,
                    "В доступе отказано: {2} {3}\n user_id = {0};\n user_username = {1}.".format(
                        message.from_user.id,
                        message.from_user.username or '???',
                        message.from_user.first_name or '???',
                        message.from_user.last_name or '???',
                    )
                )
                return False
            else:
                return fn(*args, **kwargs) or True
        return wrapper
