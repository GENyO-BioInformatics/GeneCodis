# Data Base

## [PostgreSQL 12](https://www.postgresql.org/download/linux/ubuntu/)
### Installation
```shell
# https://www.postgresql.org/download/linux/ubuntu/
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get install postgresql-12
sudo su postgres
psql
CREATE DATABASE genecodisdb;
CREATE USER genecodis WITH SUPERUSER ENCRYPTED PASSWORD '<---->';
GRANT ALL PRIVILEGES ON DATABASE genecodisdb TO genecodis;
```
### Maintenance
```shell
sudo -i -u postgres
psql # enter the server as sudo postgres
\l # check databases
\c {db_name} # check or change to db_name
\conninfo # check actual connection to db_name
\dt # check tables of db_name
\du # check existing users

# Export DB
pg_dump dbnaname > outfile
# Import DB
psql genecodisdb < outfile
```
### Creation of SQL thingies
```shell
DROP USER myuser;
DROP DATABASE mydb;

createuser --interactive # genecodis / n / s / n # USER OF THE SYSTEM
\conninfo
# Está conectado a la base de datos «genecodis» como el usuario «genecodis» a través del socket en «/var/run/postgresql» port «5432»
```
