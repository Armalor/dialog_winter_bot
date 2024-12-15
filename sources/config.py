import inspect
from os import path
from os.path import isfile, join
import json
from mergedeep import merge

# AttrDict перестал поддерживаться на версии 3.8, для более высоких версий часть модулей в collections
# переползли в другой пакет:
try:
    from attrdict import AttrDict
except ImportError:
    import collections.abc
    collections.Mapping = collections.abc.Mapping

    collections.MutableMapping = collections.abc.MutableMapping
    collections.Iterable = collections.abc.Iterable
    collections.MutableSet = collections.abc.MutableSet
    collections.Callable = collections.abc.Callable
    collections.Sequence = collections.abc.Sequence
    from attrdict import AttrDict


class Config:
    """
    version: 2.1.1
    2.0: Добавлены подстановочные значения __path__ и __file__ для работы с логами.
    2.1: AttrDict — теперь можем обращаться к элементам конфига как к атрибутам класса.
    """
    __instance = None
    __config = None
    __path = None
    __file = None

    def __init__(self, config_path=None):
        if not Config.__instance:
            Config.__config = {}
            config_files = ['config.production.json', 'config.local.json']

            stack = inspect.stack()[-1]
            # Это ВСЕГДА вызывающий файл:
            Config.__file = stack.filename

            if config_path is None:
                # Здесь мы получили конечный фрейм стека вызовов.
                # Неявно подразумеваем, что рядом с вызвавшим файлом stack.filename лежат config.***.json:
                Config.__path = path.dirname(path.abspath(Config.__file))
            else:
                Config.__path = config_path

            # Прежде всего цепляем базовый конфиг, который лежит в той же папке, что и текущий файл config.py:
            for config_file in [join(path.dirname(__file__), f) for f in config_files]:
                # Подгружаем конфиг. Может отсутствовать 'config.local.json', который на прод не переносится
                if isfile(config_file):
                    with open(config_file, encoding='utf-8') as json_file:
                        merge(Config.__config, json.load(json_file, object_hook=self.use_placeholders))

            for config_file in [join(Config.__path, f) for f in config_files]:
                # Подгружаем конфиг. Может отсутствовать 'config.local.json', который на прод не переносится
                if isfile(config_file):
                    with open(config_file, encoding='utf-8') as json_file:
                        merge(Config.__config, json.load(json_file, object_hook=self.use_placeholders))

            # Замыкаем конфиг атрибутивным словарем:
            Config.__config = AttrDict(Config.__config)

            # Перестраховка, чтобы singleton работал и в случае
            # а) conf = Config().config
            # и в случае
            # б) conf = Config.get_instance().config
            # Если этого не сделать, то случай a) не сформирует __instance
            # и в ситуации "вызов через б) после вызова через а)" получатся два развязанных конфига
            # т.к. в обоих вызовах выполнится "if not Config.__instance"
            Config.__instance = self

    def use_placeholders(self, _dict):
        for placeholder, substitution in self.placeholders.items():
            for k, v in _dict.items():
                if isinstance(v, str) and placeholder in v:
                    replaced = v.replace(placeholder, substitution)

                    # Могут использоваться псевдопути типа «../», заменяем:
                    if placeholder in ['{__file__}', '{__path__}']:
                        replaced = path.abspath(replaced)

                    _dict[k] = replaced
        return _dict

    @property
    def placeholders(self):
        return {
            '{__file__}': self.file,
            '{__path__}': self.path,
        }

    @placeholders.setter
    def placeholders(self, _):
        raise ValueError("Can't set placeholders")

    @classmethod
    def get_instance(cls, config_path=None):
        if not cls.__instance:
            cls.__instance = cls(config_path)
        return cls.__instance

    @classmethod
    def reset(cls):
        """Позволяем перезагрузить конфиг снова: нужно для задач нагрузочного тестирования в случае, когда
        последовательно тянем несколько файлов из разных папок с разными config.production.json
        """
        cls.__instance = None

    @property
    def config(self):
        return Config.__config

    @property
    def path(self):
        return Config.__path

    @path.setter
    def path(self, _):
        raise ValueError("Can't set config path value otherwise as in the constructor")

    @property
    def file(self):
        return Config.__file

    @file.setter
    def file(self, _):
        raise ValueError("Can't set config file value explicitly")

