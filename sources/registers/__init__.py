from .register import Register, register_callback
# Если не подключить здесь наследников, то класс-предок из не увидит в factory
from .register_student import RegisterStudent
from .register_friend import RegisterFriend
from .register_teacher import RegisterTeacher
