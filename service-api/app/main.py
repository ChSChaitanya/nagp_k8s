"""
Main application module for NAGP Service API.
"""
from flask import Flask
from app.routes import api
from app.database import db_pool, init_database


def create_app():
    """Application factory pattern for Flask app creation."""
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Initialize database pool and seed data on startup
    with app.app_context():
        try:
            db_pool.init_pool()
            init_database()
        except Exception as e:
            print(f"Warning: Could not initialize database on startup: {e}")
            print("Database will be initialized on first request.")
    
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
