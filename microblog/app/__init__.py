from flask import Flask
from elasticsearch import Elasticsearch as El
from .extensions import db, mail, bootstrap, moment, migrate, babel, login, stream_handler, file_handler
import logging
# from microblog import cli
from .config import Config


@babel.localeselector
def get_locale():
    # return request.accept_languages.best_match(flask_app.config['LANGUAGES'])
    return 'en'


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates') #
    app.config.from_object(config_class)
    # commands
    # cli.register(microblog)
    # Initialize extensions
    initialize_extensions(app)

    # Register blueprints
    register_blueprints(app)
    app.elasticsearch = El([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None

    # logging

    if app.config.get('LOG_TO_STDOUT'):
        # from microblog.extensions import stream_handler
        app.logger.addHandler(stream_handler)
    else:
        # from microblog.extensions import file_handler
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Microblog startup.")

    return app


def register_blueprints(flask_app):
    from .errors import bp as error_bp
    flask_app.register_blueprint(error_bp, url_prefix='/errors')

    from .auth import bp as auth_bp
    flask_app.register_blueprint(auth_bp, url_prefix='/auth')

    from .core import bp as core_bp
    flask_app.register_blueprint(core_bp, url_prefix='/')


def initialize_extensions(flask_app):
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    login.init_app(flask_app)
    mail.init_app(flask_app)
    bootstrap.init_app(flask_app)
    moment.init_app(flask_app)
    babel.init_app(flask_app)




