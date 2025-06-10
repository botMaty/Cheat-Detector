from flask import Flask, jsonify, render_template, request
from .config import Config
from .extensions import cors
from .routes.auth import auth_bp
from .routes.main import main_bp
import logging
from logging.handlers import RotatingFileHandler
import os
from werkzeug.exceptions import HTTPException

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize logging
    if not app.debug:
        log_dir = os.path.join(app.root_path, '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10000,
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.ERROR)

    # Initialize extensions
    cors.init_app(app, resources={r"/cheat_detection": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]}})

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    # Global exception handlers
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle HTTP exceptions (e.g., 404, 403, 400, 500)."""
        app.logger.error(f"HTTPException: {str(e)}")
        response = {
            'error': e.name,
            'message': e.description,
            'status_code': e.code
        }
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(response), e.code
        return render_template(f'errors/{e.code}.html', error=response), e.code

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle all unhandled exceptions to prevent app crashes."""
        app.logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
        response = {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later.',
            'status_code': 500
        }
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(response), 500
        return render_template('errors/500.html', error=response), 500

    return app