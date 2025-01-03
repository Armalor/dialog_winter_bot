from pydantic import Field
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


class RateModel(CommonModel):

    TABLE: ClassVar[str] = 'rates'
    PKEY: ClassVar[set] = {'id', 'friend_idx', 'checkpoint'}

    id: int = Field()
    friend_idx: int = Field(
        default=0,
        description="По сути это индекс в списке StudentsModel[id], где 0 — регистрация слушателя, больше 0 — друзей"
    )
    checkpoint: str = Field()
    rate: int = Field()


if __name__ == '__main__':
    config = Config().config
