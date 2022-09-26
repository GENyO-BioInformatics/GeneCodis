# GeneCodis4.0

GeneCodis4.0 (GC4) is divided in:
- Database (postgresql)
- Website (HTML, JS *(ejs + vanilla + cdn plugins)*, CSS *(bulma y custom)*)
- Server (nginx + gunicorn)
- Application (python flask)

## System installation requirements
* python >= 3.8
* python-dev >= 3.8
* nginx
* nodejs

## Application set up
### 1 Clone repo and Install python dependencies
```shell  
# 1º clone and access this repo in your machine
git clone https://github.com/GENyO-BioInformatics/GeneCodis4.0.git
cd GeneCodis4.0
# 2º create and activate virtual environment
python3.8 -m venv venv
source venv/bin/activate
# 3º install pip-tools  
pip install pip-tools
pip-compile # reads requirements.in and create requirements.txt
pip-sync # installs requirements.txt
```
### 2 Create .env
.env is a hidden file that create environment variables (i.e. private passwords)
that will be used by GC4.

1- Create manually .private (credentials)  
```
DB_NAME=
DB_USER=
DB_PSWD=
MAIL2_NAME=
MAIL_SERVER=
MAIL_USE_TLS=
MAIL_PORT=
MAIL_USE_SSL=
MAIL_USERNAME=
MAIL_PASSWORD=
```
2- Create .env
```shell  
python envgenerator.py <prod|preprod|laptop|workstation>
# it adds public variables determined by the script argument
# which are the configs needed in each machine
# and finally concatenate those in .private
```

### 3 Create and Start gunicorn and nginx service
```shell  
# 1º copia y pega las configs (ajustadas a tu máquina)
cp configs/gunicorn.service /etc/systemd/system/gunicorn.service
cp configs/nginx.service /etc/systemd/system/nginx.service
# If everything is properly installed and configured you can directly
# initiate GeneCodis4
python gc4services.py enable all # nginx & gunicorn starts with the machine
# enable only if it is the first time that you initiates GC4
python gc4services.py start all # nginx & gunicorn starts
# python gc4services.py restart all # stop and start nginx & gunicorn
```
##### Gunicorn useful commands
```shell
kill -TTIN $masterpid ## add worker
kill -TTOU $masterpid ## remove worker
```

### 4 Generate GeneCodis4 database

Follow the instructions in db/README.md

### 5 GeneCodis4 should be up and running

## Application folders and helper scripts
- gc4app
  - API with the functionalities to perform GC4 analyses (backend)
- db
  - obtain all the associations between genes and annotations
- web (frontend)
  - create static page and templates for the results
- configs
  - internal configs of gunicorn and nginx
- GeneCodis4.py
  - You can call it with the python interpreter to work in local debug mode.
- wsgi.py
  - This is used by Gunicorn to initiate the APP.
- toProduction.py
  - Call the website renderer, plus some tweaks, and performs a cache boost (updating all web assets)
- GC4programmatic.py and .R
  - Scripts to programatically handle the GC4 API
- relaunchJob.py
  - Script used by GC4 app to perform an analysis. It uses a JSON with the parameters needed.
