## TODO
http://flask.pocoo.org/docs/1.0/tutorial/deploy/
____________________
# API

Developed with the latest python (>= 3.7)

```shell
yum install gcc openssl-devel bzip2-devel libffi-devel
cd /usr/src
wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz
tar xzf Python-3.7.3.tgz
cd Python-3.7.3
./configure --enable-optimizations
make altinstall
# log out shh and enter back again
```
#### Python Modules Used *(pip freeze in venv)*
```
Flask
  Jinja2
  MarkupSafe
  Werkzeug
  Click
  itsdangerous
flask-marshmallow
  marshmallow
Flask-RESTful
  aniso8601
Flask-WTF
  WTForms
numpy
pandas
  python-dateutil
  pytz
  six
psycopg2
psycopg2-binary
```

# Source
