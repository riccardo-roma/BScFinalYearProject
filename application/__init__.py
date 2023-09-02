from flask import Flask
from .main import main
from .auth import auth

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "b7036a09b5e3096d9765a846c0def159180b67801fcadb9b"

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
