from pydantic import Field, BaseModel, ConfigDict
from typing import Optional, ClassVar

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from config import Config
from models.common import CommonModel
from connector import DBConnector
# ~Локальный импорт


class StudentModel(CommonModel):
    # model_config = ConfigDict(from_attributes=True)

    TABLE: ClassVar[str] = 'students'
    PKEY: ClassVar[set] = {'id', 'friend_idx'}

    id: int = Field()
    friend_idx: int = Field(
        default=0,
        description="По сути это индекс в списке StudentsModel[id], где 0 — регистрация слушателя, больше 0 — друзей"
    )
    name: Optional[str] = Field(default=None, description="ФИО целиком")
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
        # name='Афанасьев Александр',
        # school='7',
        # cls='11',
    )

    print(u1)

    u1.load()

    print(u1)

    # u1.__dict__.update({
    #     'name': 'Афанасьев Александр',
    #     'school': '7',
    #     'cls': '11a',
    # })
    #
    # u1.store()


