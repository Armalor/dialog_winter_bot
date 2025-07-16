drop table if exists students cascade;
create table students (
    id                  int8 not null,
    friend_idx          int not null,
    surname             varchar(255) null,
    name                varchar(255) null,
    checkpoints         varchar(255)[] null,
    constraint students_pkey primary key (id, friend_idx)
);

drop table if exists checkpoints cascade;
drop table if exists checkpoints2 cascade;
drop type if exists timing_enum;
create type timing_enum as enum (
    'minimum', 'maximum'
);

create table checkpoints(
    name                varchar(255) null,
    timing              timing_enum not null default 'maximum',
    students            jsonb not null default '[]'::jsonb,
    total               int null,
    constraint checkpoints_pkey primary key (name)
);

create table checkpoints2(
    name                varchar(255) null,
    timing              timing_enum not null default 'maximum',
    students            jsonb not null default '[]'::jsonb,
    total               int null,
    constraint checkpoints2_pkey primary key (name)
);

insert into checkpoints (name, students) values
    ('Нейросеть', '[]'::jsonb),
    ('Пойми меня', '[]'::jsonb),
    ('Сломанный телефон', '[]'::jsonb),
    ('Принтер', '[]'::jsonb),
    ('Чайная Церемония', '[]'::jsonb),
    ('Марионетка', '[]'::jsonb),
    ('Крокодил', '[]'::jsonb),
    ('Стикеры', '[]'::jsonb);

insert into checkpoints2 (name, students) values
    ('Альфа', '[]'::jsonb),
    ('Бета', '[]'::jsonb),
    ('Гамма', '[]'::jsonb),
    ('Дельта', '[]'::jsonb);


drop table if exists teachers;
create table teachers (
    id                  int8 not null,
    name                varchar(255) null,
    checkpoint          varchar(255) null,
    checkpoint2          varchar(255) null,
    constraint teachers_pkey primary key (id),
    constraint teachers_checkpoints_fkey foreign key (checkpoint)
        references checkpoints (name) on delete set null on update cascade,
    constraint teachers_checkpoints2_fkey foreign key (checkpoint2)
        references checkpoints2 (name) on delete set null on update cascade
);