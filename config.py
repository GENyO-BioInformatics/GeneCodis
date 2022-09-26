import os
from dotenv import load_dotenv
load_dotenv()

MAIL_USERNAME = os.getenv('MAIL_USERNAME') # "bioinfo@genyo.es"
MAIL_SERVER = os.getenv('MAIL_SERVER') # 'gensl015.genyo.es'
MAIL_USE_TLS = bool(int(os.getenv('MAIL_USE_TLS'))) # True
MAIL_USE_SSL = bool(int(os.getenv('MAIL_USE_SSL'))) # False
MAIL_PORT = int(os.getenv('MAIL_PORT')) # 587
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY') # 'qpwoeiruty' # pasar como variable de entorno
