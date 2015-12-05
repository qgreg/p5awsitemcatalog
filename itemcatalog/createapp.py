from flask import Flask
from flask_wtf.csrf import CsrfProtect

# Get ready to load CSRF protection
csrf = CsrfProtect()


def create_app(config_filename):
    """Creates and configures the Flask app, including initiating the database,
    registering the login_blueprint and cateogry blueprints, and establishes
    CSRF protection.

    Args:
        config_filename:  the configuration filename

    Returns:
        The Flask app.
    """
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)

    # Initiate the database
    from itemcatalog.category.models import db
    db.init_app(app)

    # Register the login blueprint that manages user Google and Facebook logins
    from itemcatalog.login.views import login_blueprint
    app.register_blueprint(login_blueprint)

    # Register the category blueprint that manages category and item CRUD
    from itemcatalog.category.views import category
    app.register_blueprint(category)

    # Establish CSRF protection but exempt the login blueprint
    csrf.init_app(app)
    csrf.exempt(login_blueprint)

    return app
