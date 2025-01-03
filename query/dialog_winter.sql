drop table if exists students cascade;
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
    students            jsonb not null default '[]'::jsonb,
    kids                boolean not null default false,
    total               int null,
    constraint checkpoints_pkey primary key (name)
);

insert into checkpoints (name, students) values
    ('Быки и коровы', '[]'::jsonb),
    ('Тяжун', '[]'::jsonb),
    ('Ксерокс', '[]'::jsonb),
    ('Водосток', '[]'::jsonb),
    ('Словари', '[]'::jsonb),
    ('Городки лабиринт', '[]'::jsonb),
    ('Большие палки', '[]'::jsonb),
    ('Большой мемори с загадками', '[]'::jsonb),
    ('Большой Эрудит', '[]'::jsonb);


drop table if exists teachers;

create table teachers (
    id                  int8 not null,
    name                varchar(255) null,
    checkpoint          varchar(255) null,
    kids                bool not null default false,
    constraint teachers_pkey primary key (id),
    constraint teachers_checkpoints_fkey foreign key (checkpoint)
        references checkpoints (name) on delete set null on update cascade
);

drop table if exists rates;
create table rates (
    id                  int8 not null,
    friend_idx          int not null,
    checkpoint          varchar(255) null,
    rate                int not null,
    constraint rates_pkey primary key (id, friend_idx, checkpoint),
    constraint rates_students_fkey foreign key (id, friend_idx)
        references students (id, friend_idx) on delete cascade on update cascade,
    constraint rates_checkpoints_fkey foreign key (checkpoint)
        references checkpoints (name) on delete cascade on update cascade
);