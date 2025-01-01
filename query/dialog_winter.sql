drop table if exists students;

create table students (
    id                  int8 not null,
    friend_idx          int not null,
    name                varchar(255) null,
    school              varchar(255) null,
    cls               varchar(255) null,
    checkpoints         varchar(255)[] null,
    constraint students_pkey primary key (id, friend_idx)
);