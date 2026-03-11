from flask import Flask
from app.config import config
from app.extensions import db, migrate, jwt, bcrypt, cors, mail

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    mail.init_app(app)
    
    from app.frontend.login_manager import login_manager
    login_manager.init_app(app)
    
    # Load User for Flask-Login
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints safely here later
    from app.api import bp as api_bp
    app.register_blueprint(api_bp)
    
    from app.frontend import bp as frontend_bp
    app.register_blueprint(frontend_bp)
    
    from app.frontend.report_routes import bp_reports
    app.register_blueprint(bp_reports)
    
    from app.frontend.portal_routes import bp_portal
    app.register_blueprint(bp_portal)
    
    from app.frontend.appointment_routes import bp_appointments
    app.register_blueprint(bp_appointments)
    
    from app import models


    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'api': 'Diagnostic Software API'}

    return app
