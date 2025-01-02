drop table if exists students;
create table students (
    id                  int8 not null,
    friend_idx          int not null,
    surname             varchar(255) null,
    name                varchar(255) null,
    school              varchar(255) null,
    cls               varchar(255) null,
    checkpoints         varchar(255)[] null,
    constraint students_pkey primary key (id, friend_idx)
);

drop table if exists checkpoints cascade;
drop type if exists timing_enum;
create type timing_enum as enum (
    'minimum', 'maximum'
);

create table checkpoints(
    name                varchar(255) null,
    timing              timing_enum not null default 'maximum',
    students            jsonb null,
    kids                boolean not null default false,
    total               int null,
    constraint checkpoints_pkey primary key (name)
);

insert into checkpoints (name) values
    ('Быки и коровы'),
    ('Тяжун'),
    ('Ксерокс'),
    ('Водосток'),
    ('Словари'),
    ('Городки лабиринт'),
    ('Большие палки'),
    ('Большой мемори с загадками'),
    ('Большой Эрудит');


drop table if exists teachers;

create table teachers (
    id                  int8 not null,
    name                varchar(255) null,
    checkpoint          varchar(255) null,
    constraint teachers_pkey primary key (id),
    constraint teachers_checkpoints_fkey foreign key (checkpoint)
        references checkpoints (name) on delete set null on update cascade
);