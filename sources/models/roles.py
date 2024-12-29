from enum import Enum

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
# ~Локальный импорт


class RolesEnum(str, Enum):
    STUDENT = 'student'
    FRIEND = 'friend'
    TEACHER = 'teacher'
