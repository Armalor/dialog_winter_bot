### Установка Постгреса
```
apt install postgresql postgresql-contrib
apt install pgadmin4
systemctl start postgresql.service
```

### Установка PgAdmin
```
curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg
sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'
apt install pgadmin4

```

### После установки Постгреса в pg_hba.conf меняем уровень доступа для пользователя postgres с peer на trust:
https://stackoverflow.com/questions/18664074/getting-error-peer-authentication-failed-for-user-postgres-when-trying-to-ge

```
pg_hba: /etc/postgresql/[version]/main/pg_hba.conf (тут есть) и, возможно, /var/lib/pgsql/data/pg_hba.conf (не проверял).

nano /etc/postgresql/16/main/pg_hba.conf
```

### Меняем пароль Постгреса:

Рестартнем сервис, чтобы подцепились изменения из pg_hba.conf:
```
systemctl restart postgresql.service
```


```
psql postgres postgres
```

Далее в psql-консоли:

```
\password postgres
```

### В ph_hba.conf вместо trust пишем md5, снова рестартим Постгрес

### Создаем базу

```
psql -U postgres -c 'create database dialog_2025_summer_first_day'
```


### Создаем таблицы
```
psql -U postgres -d dialog_2025_summer_first_day -a -f /var/dialog_bot/query/dialog_2025_summer_first_day.sql
```

### Заходим

```
psql dialog_2025_summer_first_day postgres 
```
