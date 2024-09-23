# Third-party Imports
from flask import Flask

from .tea.params import PATH


class DefaultConfig:
    UPLOAD_FOLDER = PATH['TEXTS']
    SECRET_KEY = "abcd"

def create_app(config=None): 
    app = Flask(__name__)
    config = DefaultConfig if not config else config
    app.config.from_object(config)

    from .routes import main
    app.register_blueprint(main, url_prefix='/tea/')
    
    return app