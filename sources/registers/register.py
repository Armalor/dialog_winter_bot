from abc import ABC, abstractmethod
from typing import Optional, Type

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from models import RolesEnum
# ~Локальный импорт


class RegisterNotFoundException(Exception):
    pass


class Register(ABC):

    role: Optional[RolesEnum] = None

    def __init__(self):
        ...

    @classmethod
    def factory(cls, role: RolesEnum) -> 'Register':

        classes: dict[str, Type[cls]] = {c.role: c for c in cls.__subclasses__()}
        class_ = classes.get(role, None)
        if class_ is not None:
            return class_()

        raise RegisterNotFoundException
