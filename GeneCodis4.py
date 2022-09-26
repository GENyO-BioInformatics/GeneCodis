# -*- coding: utf-8 -*-
from dotenv import load_dotenv
load_dotenv()
import gc4app, os
from gc4app import factory


app = factory.create_app()

if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_HOST"),
    port=os.getenv("FLASK_PORT"),
    debug=bool(int(os.getenv("FLASK_DEBUG"))))

