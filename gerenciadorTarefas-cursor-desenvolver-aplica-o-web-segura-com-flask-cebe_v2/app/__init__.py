import os
from flask import Flask
from dotenv import load_dotenv
from .config import Config
from .extensions import db, migrate, login_manager, csrf, mail, jwt

def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True, static_folder="static", template_folder="templates")
    app.config.from_object(Config())

    # Ensure instance folder exists - CORREÇÃO IMPORTANTE
    instance_path = app.instance_path
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"✅ Created instance folder: {instance_path}")
    os.chmod(instance_path, 0o755)  # Dar permissões

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)

    # Importar blueprints
    from .controllers.auth import auth_bp
    from .controllers.tasks import tasks_bp
    from .controllers.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Importar User
    from .models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    # Criar tabelas automaticamente
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            # Não levante a exceção para permitir que o app rode

    return app
