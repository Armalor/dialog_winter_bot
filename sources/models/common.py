import json
from pydantic import BaseModel, ConfigDict
from typing import Optional, Union, ClassVar, TYPE_CHECKING
try:
    from typing_extensions import Self
except ImportError:
    from typing import Self

from enum import IntEnum, Enum
from psycopg2.extensions import cursor
from pprint import pprint

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny


# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent
sys.path.append(__root__.__str__())
from connector import db_connector
# ~Локальный импорт


class CommonModel(BaseModel):
    """
    Обобщенные параметры модели: таблица, первичный ключ, обмен данными с базой.
    """

    # Даем возможность в конструкторе загружать значения не только по алиасам, но и по базовым именам
    # (https://stackoverflow.com/questions/69433904/assigning-pydantic-fields-not-by-alias):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    TABLE: ClassVar[str] = None
    PKEY: ClassVar[set] = None

    def dumps(self, exclude: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']] = None) -> dict:
        return json.loads(self.json(exclude=exclude))

    @property
    def __insert(self):

        cols = self.dict(exclude=self.PKEY).keys()

        placeholders = map(lambda x: f'%({x})s', cols)

        if self.PKEY is None:
            on_conflict = 'do nothing'
        else:
            conflict_placeholders = map(lambda x: f'{x} = EXCLUDE.{x})', cols)
            on_conflict = f"""({", ".join(self.PKEY)}) do update set 
                {', '.join(conflict_placeholders)}
            """

        _insert = f'''
            insert into {self.TABLE} ({', '.join(cols)}) values ({', '.join(placeholders)})
            on conflict {on_conflict} 
            
            returning {self.TABLE}.*
        '''

        return _insert, self.dict()

    @property
    def __delete(self):

        pkey = map(lambda x: f'{x} = %({x})s', self.PKEY)

        _delete = f'''
            delete from {self.TABLE}
            where 
                {' and '.join(pkey)}
            returning {self.TABLE}.*
        '''

        return _delete, self.dict()

    @property
    def __find_by_pkey(self) -> tuple:

        if self.PKEY is None:
            raise NotImplementedError(f'Primary key for table {self.TABLE} is None')

        if any(self.__dict__.get(k) is None for k in self.PKEY):
            raise ValueError(f'Primary key ({", ".join(self.PKEY)}) for table {self.TABLE} is not set in current model')

        pkey = map(lambda x: f'{x} = %({x})s', self.PKEY)
        return f'''select * from {self.TABLE} as t where {' and '.join(pkey)}''', self.dict()

    @db_connector
    def load(self, cur: cursor = None) -> Self:
        cur.execute(*self.__find_by_pkey)
        ret = cur.fetchone()
        # TODO: Вариант, что по первичному ключу ничего не нашли, пока не предусмотрен:
        self.__dict__.update(ret)

        return self

    @db_connector
    def store(self, cur: cursor = None) -> Self:

        # 1. Если первичного ключа нет, то это точно INSERT, т.к. других вариантов быть не может.
        # 2. Если первичный ключ есть, но не задан в модели, это значит, что он генерируется последовательностью.
        cur.execute(*self.__insert)
        ret = cur.fetchone()

        self.__dict__.update(ret)

        return self

    @db_connector
    def delete(self, cur: cursor = None) -> Self:
        cur.execute(*self.__delete)
        ret = cur.fetchone()
        # TODO: Вариант, что по первичному ключу ничего не нашли, пока не предусмотрен:
        self.__dict__.update(ret)

        return self
