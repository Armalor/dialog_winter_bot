import json

from pydantic import Field, BaseModel, computed_field
from typing import Optional, ClassVar
from functools import reduce
from pprint import pprint
from enum import Enum

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from config import Config
from models.students import StudentModel
from models.common import CommonModel
# ~Локальный импорт


class TimingEnum(str, Enum):
    MIN = 'minimum'
    MAX = 'maximum'


class CheckpointModel(CommonModel):

    TABLE: ClassVar[str] = 'checkpoints'
    PKEY: ClassVar[set] = {'name', }

    name: str = Field(),
    timing: TimingEnum = Field(default=TimingEnum.MAX)
    students: list[list[StudentModel]] = Field(default_factory=list)
    kids: bool = Field(default=False)

    @computed_field
    @property
    def total(self) -> int:
        return reduce(lambda x, y: x + y, map(lambda z: len(z), self.students), 0)

    @property
    def _upsert(self):
        _upsert, model_dump = super()._upsert

        model_dump['students'] = json.dumps(model_dump['students'], ensure_ascii=False, sort_keys=False)

        return _upsert, model_dump


if __name__ == '__main__':
    config = Config().config

    model = CheckpointModel(
        name='Критическая информация',
        # students=[
        #     [StudentModel(id=1, surname='Зиновьева', name='Зина'), StudentModel(id=2, surname='Иванов', name='Иван'), StudentModel(id=3, surname='Петров', name='Петр')],
        #     [StudentModel(id=4, surname='Кириллов', name='Кирилл'), StudentModel(id=5, surname='Романов', name='Роман')],
        # ]
    )

    print(model, id(model))

    model.load()

    pprint(model.model_dump(), width=128)
    print(model.total)

    print(model, id(model))

    # model.store()
    # pprint(model.model_dump(), width=128)
