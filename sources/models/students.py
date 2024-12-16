from pydantic import Field, BaseModel
from typing import Optional


# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from config import Config
# ~Локальный импорт


class StudentModel(BaseModel):
    id: Optional[int] = Field(default=None)
    surname: str = Field()
    name: str = Field()
    school: Optional[str] = Field(default=None)
    class_: Optional[str] = Field(default=None)
    checkpoints: list[str] = Field(default_factory=list)

    # def __str__(self):
    #     return f'{self.surname} {self.name}'


if __name__ == '__main__':
    config = Config().config

    u1 = StudentModel(
        id=1,
        surname='Афанасьев',
        name='Александр',
    )

    print(u1)
    j = u1.model_dump_json().encode()
    print(j, type(j))

