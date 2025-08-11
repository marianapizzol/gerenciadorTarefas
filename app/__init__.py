import os
from flask import Flask
from dotenv import load_dotenv
from .config import Config
from .extensions import db, migrate, login_manager, csrf, mail, jwt
from .models import User


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True, static_folder="static", template_folder="templates")

    app.config.from_object(Config())

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)

    # Blueprints
    from .controllers.auth import auth_bp
    from .controllers.tasks import tasks_bp
    from .controllers.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    return app