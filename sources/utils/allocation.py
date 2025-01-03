from pprint import pprint
import random

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).resolve().parent.parent
sys.path.append(__root__.__str__())
from utils._students import students_list
from utils._checkpoints import checkpoints_list
from models import StudentModel, CheckpointModel
from connector import DBConnector
from registers import RegisterStudent
# ~Локальный импорт


class DekulakizationException(Exception):
    """Бросается когда бедный КП раскулачил богатый."""
    pass


def allocation_step(students: list[StudentModel], checkpoints: list[CheckpointModel], kids_point_idx: int = 0) -> tuple[list[StudentModel], list[CheckpointModel]]:

    random.shuffle(students)
    students_len = len(students)
    checkpoints_len = len(checkpoints)

    allocated_students = []

    for idx, checkpoint in enumerate(checkpoints):
        checkpoint.students.append([])
        checkpoint.kids = idx == kids_point_idx

    checkpoint_idx = kids_point_idx

    # Нулевой шаг аллокации:
    # Если это предпоследний тик, то КП, который на последнем тике пустует, обязан добрать слушателей
    # до предела. Иначе, на последнем тике аллокацию вообще не удастся завершить: останутся несколько студентов,
    # которые были на всех КП, кроме последнего — не участвующего сейчас в аллокации.
    if checkpoints[-2].kids:
        checkpoint = checkpoints[-1]
        print(f'ЭТО ПРЕДПОСЛЕДНИЙ ТИК! Последний КП — {checkpoint.name} — должен собрать ВСЕХ своих слушателей!')
        for student in students:
            if checkpoint.name not in student.checkpoints and student not in allocated_students:
                student.checkpoints.append(checkpoint.name)
                allocated_students.append(student)
                checkpoint.students[-1].append(student)

    # Первый шаг аллокации: КП по очереди выбирают студентов. Проблема: в «остатоке» может быть ситуация, когда
    # студенты, подходяшие для «бедного» КП, уже разобраны «богатыми»...
    while len(allocated_students) < students_len:
        checkpoint_idx = (checkpoint_idx + 1) % checkpoints_len

        checkpoint = checkpoints[checkpoint_idx]

        # На этом КП сейчас мелкие дети, он никого не выбирает:
        if checkpoint.kids:
            continue

        for student in students:
            if checkpoint.name not in student.checkpoints and student not in allocated_students:
                student.checkpoints.append(checkpoint.name)
                allocated_students.append(student)
                checkpoint.students[-1].append(student)
                break

    students_minimum = students_len // (checkpoints_len - 1)
    # ... Поэтому делим все КП на группы, в которых студентов больше, чем students_minimum (богатые), и меньше (бедные).
    poor = []
    rich = []
    for checkpoint in checkpoints:
        if checkpoint.kids:
            continue

        if len(checkpoint.students[-1]) < students_minimum:
            poor.append(checkpoint)
        if len(checkpoint.students[-1]) > students_minimum:
            rich.append(checkpoint)

    for p in poor:
        print(f'БЕДНЫЙ КП: {p.name} ({p.total}) {len(p.students[-1])}')

    # Здесь важно забрать не просто у богатого, а у самого богатого за все тики:
    rich.sort(key=lambda x: x.total, reverse=True)

    if poor:
        print('')
        for r in rich:
            print(f'БОГАТЫЙ КП: {r.name} ({r.total}){len(r.students[-1])}')
            ...

    # ВНИМАНИЕ! НЕ МОЖЕМ раскулачивать последний КП на предпоследнем тике!!!
    if checkpoints[-2].kids and checkpoints[-1] in rich:
        print(f'НЕ МОЖЕМ раскулачить последний кп — {checkpoints[-1].name} — на предпоследнем тике!')
        rich.remove(checkpoints[-1])

    for p in poor:
        try:
            for r in rich:
                for student in r.students[-1]:
                    if p.name not in student.checkpoints:
                        student.checkpoints.remove(r.name)
                        r.students[-1].remove(student)

                        student.checkpoints.append(p.name)
                        p.students[-1].append(student)

                        rich.remove(r)

                        raise DekulakizationException(f'Раскулачили «{r.name}» в пользу «{p.name}»')
        except DekulakizationException as dekul:
            print(dekul)

    # print(len(allocated_students), students_len)
    return allocated_students, checkpoints


def get_students_from_db() -> list[StudentModel]:
    students = []
    std_dict = RegisterStudent.load()
    for friends_group in std_dict.values():
        for std in friends_group:
            students.append(std)

    return students


def get_checkpoints_from_db() -> list[CheckpointModel]:
    checkpoints = []
    with DBConnector() as cur:
        cur.execute('select * from checkpoints order by name')
        for ch in cur.fetchall():
            checkpoints.append(CheckpointModel.model_validate(ch))

    return checkpoints


if __name__ == '__main__':

    def get_checkpoints():
        checkpoints = []
        for idx, name in enumerate(checkpoints_list, start=1):
            ch = CheckpointModel(name=name)
            checkpoints.append(ch)
        return checkpoints

    def get_students():
        students = []
        for idx, student in enumerate(students_list, start=1):
            name, surname = student.split(' ')
            st = StudentModel(
                id=idx,
                name=name,
                surname=surname,
            )

            students.append(st)

        return students

    # students = get_students()
    # pprint(students)
    students = get_students_from_db()
    pprint(students)

    # checkpoints = get_checkpoints()
    checkpoints = get_checkpoints_from_db()

    ch_names = list(map(lambda x: x.name, checkpoints))
    print(len(ch_names), ch_names)

    for tick in range(9):

        print(f'')
        print(f'')
        print(f'############ TICK {tick+1}')

        students, checkpoints = allocation_step(students, checkpoints, tick)

        # pprint(students)

        total = 0
        for ch in checkpoints:
            print('')
            print(f'{ch.name}: {ch.total}', 'ТУТ ДЕТИ!' if ch.kids else '')
            tick_students = ch.students[-1]
            surnames = list(map(lambda x: x.surname, tick_students))
            print(surnames, len(surnames))

            total += ch.total
        print(f'total: {total / (tick + 1)}')