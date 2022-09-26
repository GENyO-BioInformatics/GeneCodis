# -*- coding: utf-8 -*-
from dotenv import load_dotenv
load_dotenv()
from GeneCodis4 import app
import os

if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_HOST"),
    port=os.getenv("FLASK_PORT"),
    debug=bool(int(os.getenv("FLASK_DEBUG"))))
