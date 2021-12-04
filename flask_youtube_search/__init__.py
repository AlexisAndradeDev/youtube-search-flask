from flask import Flask
from .routes import main

app = Flask(__name__)
app.config.from_pyfile("settings.py")
app.register_blueprint(main)
