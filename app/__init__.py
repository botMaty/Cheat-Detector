from flask import Flask
from .config import Config
from .extensions import cors
from .routes.auth import auth_bp
from .routes.main import main_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    cors.init_app(app, resources={r"/cheat_detection": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]}})

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    return app