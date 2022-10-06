from flask import Flask
from flask_cors import CORS
#from .celery_utils import init_celery
from flask_mail import Mail
from flask_marshmallow import Marshmallow
import os, jinja2
from dotenv import load_dotenv
load_dotenv()
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
mail = Mail()

def create_app(appName="gc4app",mail=mail,**kwargs):
    app = Flask(appName, static_url_path=os.getenv('STATIC_URL_PATH'),
                static_folder=os.getenv('STATIC_FOLDER'))
    app.jinja_loader = jinja2.ChoiceLoader([app.jinja_loader,
                       jinja2.FileSystemLoader([
                       os.getenv('TEMPLATE_FOLDER')]
                       )])
    
    app.config.from_object('config')
    mail.init_app(app)
    CORS(app)
    from gc4app.blueprint import bp,checkstatebp,results,qc
    limiter = Limiter(app, key_func=get_remote_address,storage_uri="redis://localhost:6379",strategy="fixed-window") # or "moving-window")
    #limiter.limit("3/minute")(bp)
    #app.register_blueprint(queryTerm) 
    limiter.limit("10/minute",key_func=get_remote_address)(bp)
    app.register_blueprint(bp)
    app.register_blueprint(checkstatebp)
    app.register_blueprint(results)
    app.register_blueprint(qc)

    return app
