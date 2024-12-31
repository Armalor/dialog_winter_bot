from pydantic import Field, BaseModel, ConfigDict
from typing import Optional


# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from config import Config
from connector import DBConnector
# ~Локальный импорт


class StudentModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field()
    friend_idx: int = Field(
        default=0,
        description="По сути это индекс в списке StudentsModel[id], где 0 — регистрация слушателя, больше 0 — друзей"
    )
    surname: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    school: Optional[str] = Field(default=None)
    cls: Optional[str] = Field(default=None)
    checkpoints: list[str] = Field(default_factory=list)



    # def __str__(self):
    #     return f'{self.surname} {self.name}'


StudentsModel = dict[int, list[StudentModel]]


if __name__ == '__main__':
    config = Config().config

    u1 = StudentModel(
        id=1,
        friend_idx=0,
        surname='Афанасьев',
        name='Александр',
        school='7',
        cls='7',
    )

    print(u1)
    j = u1.model_dump_json()
    print(j, type(j))

