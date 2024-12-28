import logging


class TelegramFilter(logging.Filter):
    """
    Добавляем картинку-иконку для отображения info-error-critical в сообщении Telegram-бота.
    """

    ICON = {
        "DEBUG": "",
        "INFO": "✅",
        "WARNING": "♨",
        "ERROR": "❌",
        "CRITICAL": "☢",#☠
    }

    def filter(self, record):
        record.icon = TelegramFilter.ICON[record.levelname]
        return True
