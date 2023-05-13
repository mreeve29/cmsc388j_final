from flask import Flask, render_template
from flask_mongoengine import MongoEngine
from flask_talisman import Talisman
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

from datetime import datetime
import os
from dotenv import load_dotenv

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()

from .users.routes import users
from .restaurants.routes import restaurants

def page_not_found(e):
    return render_template("404.html"), 404

def create_app(test_config=None):
    load_dotenv()

    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        MONGODB_HOST=os.environ.get("MONGODB_HOST")
    )

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    #csp stuff
    csp = {
        'default-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'data:'
        ],
        'style-src':[
            '\'unsafe-inline\'',
            '\'self\'',
            'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css',
        ],
        'script-src':[
            '\'unsafe-inline\'',
            'https://code.jquery.com/jquery-3.4.1.slim.min.js',
            'https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js',
            'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js',
            'https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js',
        ],
        'frame-src':[
            '\'unsafe-inline\'',
            '*.google.com',
        ]
    }
    Talisman(app, content_security_policy=csp)

    app.register_blueprint(users)
    app.register_blueprint(restaurants)
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app
