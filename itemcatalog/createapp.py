from flask import Flask
from flask_wtf.csrf import CsrfProtect

csrf = CsrfProtect()

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)

    from itemcatalog.category.models import db
    db.init_app(app)
    db.create_all()

    from itemcatalog.login.views import login_blueprint
    app.register_blueprint(login_blueprint)

    from itemcatalog.category.views import category
    app.register_blueprint(category)

    csrf.init_app(app)

    return app