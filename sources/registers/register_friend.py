from typing import Optional

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from models import RolesEnum
from .register_student import RegisterStudent
# ~Локальный импорт


class RegisterFriend(RegisterStudent):

    role: Optional[RolesEnum] = RolesEnum.FRIEND

    title = 'Профиль друга'
