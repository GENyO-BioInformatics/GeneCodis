#!/bin/bash
echo 'activate venv'
### Activate virtual environment
source ../../venv/bin/activate
echo 'activated venv'
### Run the first module. Takes a long time
python generate_and_download_tables.py
echo 'Done generate_and_download_tables'
### Run the second module. Takes a long time
python updateGeneCodis.py
echo 'Done updateGeneCodis'
### Run the third module
python loadGeneCodistoPostgres.py
echo 'Done loadGeneCodistoPostgres'
