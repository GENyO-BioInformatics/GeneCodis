# GeneCodis4.0

## System dependencies (services that need to be up)
* python3.6 >=
    * gunicorn
    * celery + flower   
* redis
* ngix

## Redis
```shell
apt-get install redis-server
systemctl enable redis-server.service
nano /etc/redis/redis.conf
# maxmemory 1gb
# maxmemory-policy allkeys-lru
# supervised systemd
systemctl restart redis-server.service
# redis://localhost:6379//
```

## Python dependencies
```shell  
python3.7 -m venv gc4venv # create virtual environment
source gc4venv/bin/activate
pip install pip-tools
# pip-compile in dev
# pip-sync to deploy
# optional kernel for ATOM/hydrogen ONLY IN DEV!
python3.7 -m ipykernel install --user --name gc4
```

## Server
```shell
firewall-cmd --permanent --zone=public --add-port=5000/tcp
```

## NGIX
```shell
setenforce 0
setsebool -P httpd_can_network_connect 1
sudo cat /var/log/audit/audit.log | grep nginx | grep denied | audit2allow -M mynginx
sudo semodule -i mynginx.pp
```

## Python3.7
```shell
yum install gcc openssl-devel bzip2-devel libffi-devel
cd /usr/src
wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz
tar xzf Python-3.7.4.tgz
cd Python-3.7.4
./configure --enable-optimizations
make altinstall
rm /usr/src/Python-3.7.4.tgz
```

## Gunicorn
```shell
# yum install gunicorn
gunicorn --bind 0.0.0.0:5000 wsgi:app
```
