from flask import Flask, render_template, flash, redirect, request, url_for
from .extensions import db, migrate, login_manager, jwt, mail, csrf, oauth, limiter, compress
from .config import config
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_limiter.errors import RateLimitExceeded

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    oauth.init_app(app)
    limiter.init_app(app)
    compress.init_app(app)

    # Idempotent DB Upgrades
    from .utils.db_upgrade import upgrade_database
    upgrade_database(app)

    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.jobs import jobs_bp
    from .routes.recruiter import recruiter_bp
    from .routes.admin import admin_bp
    from .routes.ai import ai_bp
    from .routes.portfolio import portfolio_bp
    from .routes.resume import resume_bp
    from .routes.sprint import sprint_bp
    
    from .routes.playground import playground_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    app.register_blueprint(recruiter_bp, url_prefix='/recruiter')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(portfolio_bp, url_prefix='/portfolio')
    app.register_blueprint(resume_bp, url_prefix='/resume')
    app.register_blueprint(sprint_bp, url_prefix='/user/sprint')
    app.register_blueprint(playground_bp, url_prefix='/playground')
    
    # Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com "
            "https://cdnjs.cloudflare.com https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com "
            "https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://cdnjs.cloudflare.com; "
            "worker-src 'self' blob:;"
        )
        response.headers['Content-Security-Policy'] = csp
        if not app.debug:
            response.headers['Strict-Transport-Security'] = \
                'max-age=31536000; includeSubDomains'
        return response

    # Error Handlers
    @app.errorhandler(RateLimitExceeded)
    def handle_ratelimit(e):
        flash("Too many attempts. Please wait before trying again.", "danger")
        return redirect(request.referrer or url_for('auth.login'))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.route('/')
    def index():
        return render_template('index.html')
        
    # Logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/be_your.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Be Your startup')

    return app
