from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from hashlib import md5
from time import time
import jwt
from .extensions import db, login
from .search import add_to_index, remove_from_index, query_index

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class SearchableMixin(object):
    """
    A glue layer between the SQLAlchemy and Elasticsearch.
    """
    @classmethod
    def search(cls, expr, page, per_page):
        ids, total = query_index(cls.__tablename__, expr, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0

        when = list()
        for i in range(len(ids)):
            when.append((ids[i], i))

        return cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


association_idol_followers = db.Table('association_idol_followers',
                                      db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                                      db.Column('idol_id', db.Integer, db.ForeignKey('user.id')))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128), unique=True, index=True)
    # A user has many posts.
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # Profile
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # The idols followed by this user.
    idols = db.relationship('User',
                            secondary=association_idol_followers,
                            primaryjoin=(association_idol_followers.c.follower_id==id),
                            secondaryjoin=(association_idol_followers.c.idol_id==id),
                            backref=db.backref('followers', lazy='dynamic'),
                            lazy='dynamic'
                            )

    def __repr__(self):
        return "<User: %s>"%self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://s.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    # Follower and followed features
    def is_following(self, user):
       return self.idols.filter(
           association_idol_followers.c.idol_id == user.id
       ).count() > 0

    def follow(self, user):
        # Idolize the user
        if not self.is_following(user):
            self.idols.append(user)

    def unfollow(self, user):
        # Un-fun the user
        if self.is_following(user):
            self.idols.remove(user)

    def idols_posts(self):
        """
        Get the posts of the idols (including self) in desc order of timestamp.
        :return:
        """
        # Join table `post` and table `association_idol_followers` by idol_id and user_id in two tables, respectively.
        # Filter the joined table by follower_id and self.id.
        idol_posts = Post.query.join(association_idol_followers, (association_idol_followers.c.idol_id == Post.user_id)
                                      ).filter(association_idol_followers.c.follower_id == self.id)

        self_posts = Post.query.filter_by(user_id = self.id)

        return idol_posts.union(self_posts).order_by(Post.timestamp.desc())

    # Password resetting
    def get_reset_password_token(self, expires_in=60):
        return jwt.encode({'reset_password': self.id,
                           'exp': time()+expires_in},
                          current_app.config.get("SECRET_KEY"),
                          algorithm='HS256'
                          ).decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token,
                                 current_app.config.get("SECRET_KEY"),
                                 algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(user_id)


class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return "<Post: %s>"%self.body


# class Message(db.Model):
