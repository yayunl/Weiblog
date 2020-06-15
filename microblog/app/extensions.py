

# Flask sqlalchemy
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Flask migrate
from flask_migrate import Migrate
migrate = Migrate()

# Flask mail
from flask_mail import Mail
mail = Mail()

# Flask bootstrap
from flask_bootstrap import Bootstrap
bootstrap = Bootstrap()

# Flask moment
from flask_moment import Moment
moment = Moment()

# Flask babel
from flask_babel import Babel
from flask_babel import lazy_gettext as _I
babel = Babel()


# Flask login
from flask_login import LoginManager
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _I('Please log into access this page.')

# Logging
import logging, os
from logging.handlers import RotatingFileHandler
# from dotenv import load_dotenv
# basedir = os.path.abspath((os.path.dirname(__file__)))
# load_dotenv(os.path.join(basedir, '.env'))

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# Local logging
# if not os.path.exists('logs'):
#     os.mkdir('logs')
file_handler = RotatingFileHandler(os.environ.get('LOCAL_LOG_PATH', 'microblog.log'),
                                   maxBytes=10240,
                                   backupCount=10)
file_logging_format = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
file_handler.setLevel(logging.INFO)

