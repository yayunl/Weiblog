import os
# from dotenv import load_dotenv
basedir = os.path.abspath((os.path.dirname(__file__)))
# load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'microblog.db')

    SQLALCHEMY_TRACK_MODIFICATIONS=False

    POSTS_PER_PAGE=3

    # Flask mail
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')

    MAIL_SERVER= "smtp.googlemail.com"
    MAIL_PORT= 587
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") or True
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL") or False
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or ADMIN_EMAIL
    MAIL_PASSWORD = os.environ.get("MAIL_TOKEN")

    # Flask babel languages
    LANGUAGES = ['en', 'zh']

    # Azure translation service
    MS_TRANSLATION_KEY = os.environ.get('MS_TRANSLATION_KEY')

    # Elasticsearch
    ELASTICSEARCH_URL=os.environ.get('ELASTICSEARCH_URL')

    # Logging
    FILE_LOG_PATH= os.path.join(os.path.join(basedir, 'logs'), 'microblog.log')