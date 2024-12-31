from psycopg2 import connect
from psycopg2._psycopg import connection
from psycopg2.extensions import cursor
from psycopg2.extras import RealDictCursor
from os import path
from typing import Literal, Callable
import sys
__path__ = path.dirname(path.abspath(__file__))
sys.path.append(__path__)
from config import Config
from sshtunnel import SSHTunnelForwarder
from functools import wraps


class DBConnector:
    def __init__(self, cursor_factory=RealDictCursor, db_config_key='db', autocommit=False, name=None) -> None:
        self.config = Config.get_instance().config[db_config_key]
        self.conn: connection | Literal[False] = False
        self.cur: cursor | Literal[False] = False
        self.cursor_factory = cursor_factory
        self.autocommit = autocommit
        self.tunnel = None

        # Это — для создания server side cursor (https://www.psycopg.org/docs/usage.html#server-side-cursors) и чтения
        # из базы по кускам. После создания именованного курсора нужно задать параметр «itersize» (по умолчанию 2 000)
        self.name = name

    def __enter__(self) -> cursor:
        try:

            # ssh — мета-параметр, который мы добавляем к БД-конфигу, если хотим заходить в базу по ssh-туннелю
            ssh = self.config.get('ssh', None)
            if ssh and not self.tunnel:
                del (self.config['ssh'])  # Это нельзя убирать (sic!), иначе упадет connect(**self.config)
                self.tunnel = SSHTunnelForwarder((ssh['host'], ssh['port']),
                                            ssh_username=ssh['user'],
                                            ssh_password=ssh['password'],
                                            remote_bind_address=(ssh['remote_bind_host'], ssh['remote_bind_port']),
                                            local_bind_address=(ssh['local_bind_host'], ssh['local_bind_port']))
                self.tunnel.start()

            self.conn = connect(**self.config)

            if self.autocommit:
                self.conn.set_session(autocommit=True)

            # Если для именованного курсора не передавать withhold, и при этом курсор закрывается ПОСЛЕ commit/rollback
            # (так было сделано ранее), то «self.cur.close» вызовет ошибку
            # «psycopg2.ProgrammingError: named cursor isn't valid anymore».
            # С этим можно бороться либо для каждого курсора передавая, withhold=bool(self.name), либо (как сделали
            # сейчас) — закрывая курсор ДО закрытия транзакции, см. метод __exit__
            self.cur = self.conn.cursor(cursor_factory=self.cursor_factory, name=self.name)
        except DBConnectionError as err:
            print('Exception:', str(err))
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.conn and self.cur:
            # Курсор надо закрывать ДО завершения транзакции, иначе, при создании именованного курсора (только для них),
            # попытка закрытия будет падать с ошибкой «psycopg2.ProgrammingError: named cursor isn't valid anymore» —
            # это происходит из-за того, что именованный курсор в принципе живет только пока жива транзакция:
            # «Named cursors are usually created WITHOUT HOLD, meaning they live only as long as the current
            # transaction. Trying to fetch from a named cursor after a commit() or to create a named cursor when the
            # connection is in autocommit mode will result in an exception».
            self.cur.close()

            if exc_val is not None:
                # Считаем, если мы вылетели из with-блока с исключением, то это однозначный сигнал в базу не писать:
                self.conn.rollback()
            else:
                self.conn.commit()

            self.conn.close()


class DBConnectionError (Exception):
    pass


def db_connector(func: Callable) -> Callable:
    """Если в оборачиваемую функцию не передан курсор, то инициализируем соединение с БД"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        cursor_ = None
        for arg in args:
            if isinstance(arg, cursor):
                cursor_ = arg

        for key, arg in kwargs.items():
            # TODO: вот тут мы привязаны к имени параметра — 'cur':
            if isinstance(arg, cursor) or 'key' == 'cur':
                cursor_ = arg

        if cursor_ is None:
            with DBConnector() as cursor_:
                # TODO: вот тут мы привязаны к имени параметра — 'cur':
                kwargs['cur'] = cursor_
                ret = func(*args, **kwargs)
        else:
            ret = func(*args, **kwargs)

        return ret

    return wrapper
