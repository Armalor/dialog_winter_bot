from pydantic import Field, BaseModel, computed_field
from typing import Optional
from functools import reduce
from pprint import pprint

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from config import Config
from models.students import StudentModel
# ~Локальный импорт


class CheckpointModel(BaseModel):
    name: str = Field(),
    students: list[list[StudentModel]] = Field(default_factory=list)
    kids: bool = Field(default=False)

    @computed_field
    @property
    def total(self) -> int:
        return reduce(lambda x, y: x + y, map(lambda z: len(z), self.students))


if __name__ == '__main__':
    config = Config().config

    model = CheckpointModel(
        name='Критическая информация',
        students=[
            [StudentModel(surname='Зиновьева', name='Зина'), StudentModel(surname='Иванов', name='Иван'), StudentModel(surname='Петров', name='Петр')],
            [StudentModel(surname='Кириллов', name='Кирилл'), StudentModel(surname='Романов', name='Роман')],
        ]
    )

    pprint(model.model_dump(), width=128)
    print(model.total)
