from flask import Flask, render_template
from routes import api, init_cache
from config import Config
from utils import setup_logging
from models import Page, Post
import logging
from datetime import datetime

def init_db_indexes():
    """Initialize database indexes with proper error handling"""
    try:
        page_indexes = Page.create_indexes()
        post_indexes = Post.create_indexes()
        if page_indexes and post_indexes:
            logging.info("All database indexes created successfully")
        else:
            logging.warning("Some database indexes could not be created")
    except Exception as e:
        logging.error(f"Failed to create database indexes: {e}")
        # Don't raise here, allow the application to start even if indexes fail
        # They can be created later when the database becomes available

def create_app():
    # Setup logging first
    setup_logging()
    logging.info("Starting application initialization")

    app = Flask(__name__)
    app.config.from_object(Config)
    logging.info("Loaded configuration")

    # Initialize cache
    cache = init_cache(app)
    if cache:
        logging.info("Cache initialized successfully")
    else:
        logging.warning("Cache initialization skipped or failed")

    # Register template filters
    @app.template_filter('datetime')
    def format_datetime(value):
        if value is None:
            return ""
        return value.strftime('%Y-%m-%d %H:%M:%S')

    # Register blueprints
    app.register_blueprint(api)
    logging.info("Registered API blueprints")

    # Root route for the web interface
    @app.route('/')
    def index():
        return render_template('index.html')

    # Initialize database indexes
    with app.app_context():
        init_db_indexes()

    logging.info("Application initialization completed")
    return app

if __name__ == '__main__':
    try:
        app = create_app()
        logging.info("Starting Flask server...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logging.error(f"Failed to start application: {str(e)}")
        raise