from flask import Flask
from flask_cors import CORS
#from .celery_utils import init_celery
from flask_mail import Mail
from flask_marshmallow import Marshmallow
import os, jinja2
from dotenv import load_dotenv
load_dotenv()

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
    from gc4app.blueprint import bp
    app.register_blueprint(bp)
    CORS(app)
    
    return app
