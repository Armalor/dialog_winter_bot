from typing import Optional

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from models import RolesEnum
from .register import Register
# ~Локальный импорт


class RegisterStudent(Register):

    role: Optional[RolesEnum] = RolesEnum.STUDENT

