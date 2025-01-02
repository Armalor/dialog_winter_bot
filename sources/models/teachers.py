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


class TeacherModel(CommonModel):

    TABLE: ClassVar[str] = 'teachers'
    PKEY: ClassVar[set] = {'id', }

    id: int = Field()

    name: Optional[str] = Field(default=None)
    checkpoint: Optional[str] = Field(default=None)


if __name__ == '__main__':
    config = Config().config

    u1 = TeacherModel(
        id=1,

        # surname='Афанасьев',
        # name='Александр',
        # school='7',
        # cls='11',
    )

    print(u1)

    u1.load()

    print(u1)

    # u1.__dict__.update({
    #     'surname': 'Афанасьев',
    #     'name': 'Александр',
    #     'school': '7',
    #     'cls': '11a',
    # })
    #
    # u1.store()


