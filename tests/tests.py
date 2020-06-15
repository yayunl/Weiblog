from datetime import datetime, timedelta
import unittest
from microblog import create_app, db
from microblog import User, Post
from microblog.app.config import Config


class TestConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):

        def setUp(self):
            self.app = create_app(TestConfig)
            self.app_context=self.app.app_context()
            self.app_context.push()
            db.create_all()

        def tearDown(self):
            db.session.remove()
            db.drop_all()
            self.app_context.pop()

        def test_password_hashing(self):
            u = User(username='susan')
            u.set_password('cat')
            self.assertFalse(u.check_password('dog'))
            self.assertTrue(u.check_password('cat'))

        def test_avatar(self):
            u = User(username='john', email='john@example.com')
            self.assertEqual(u.avatar(128), ('https://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?d=identicon&s=128'))

        def test_follow(self):
            u1= User(username='john', email='john@example.com')
            u2 = User(username='susan', email='susan@example.com')
            db.session.add(u1)
            db.session.add(u2)
            db.session.commit()

            self.assertEqual(u1.idols.all(), [])
            self.assertEqual(u2.idols.all(), [])

            # Test follow
            u1.follow(u2)
            db.session.commit()

            self.assertTrue(u1.is_following(u2))
            self.assertEqual(u1.idols.count(), 1)
            self.assertEqual(u1.idols.first().username, u2.username)
            self.assertEqual(u2.followers.count(), 1)
            self.assertEqual(u2.followers.first().username, u1.username)

            # Test unfollow
            u1.unfollow(u2)
            db.session.commit()

            self.assertFalse(u1.is_following(u2))
            self.assertEqual(u1.idols.count(), 0)
            self.assertEqual(u2.idols.count(), 0)

        def test_follow_posts(self):
            # create users
            u1 = User(username='john', email='john@example.com')
            u2 = User(username='susan', email='susan@example.com')
            u3 = User(username='mary', email='mary@example.com')
            u4 = User(username='david', email='david@example.com')
            db.session.add_all([u1, u2, u3, u4])

            # create posts
            now = datetime.utcnow()
            p1 = Post(body="post from john", author=u1,
                      timestamp=now + timedelta(seconds=1))
            p2 = Post(body="post from susan", author=u2,
                      timestamp=now + timedelta(seconds=4))
            p3 = Post(body="post from mary", author=u3,
                      timestamp=now + timedelta(seconds=3))

            p4 = Post(body="post from david", author=u4,
                      timestamp=now + timedelta(seconds=2))
            db.session.add_all([p1, p2, p3, p4])
            db.session.commit()

            # create following relationship
            u1.follow(u2)
            u1.follow(u4)
            u2.follow(u3)
            u3.follow(u4)
            db.session.commit()

            # Verify the posts of the idols
            fps1 = u1.idols_posts().all()
            fps2 = u2.idols_posts().all()
            fps3 = u3.idols_posts().all()
            fps4 = u4.idols_posts().all()

            self.assertEqual(fps1, [p2, p4, p1])
            self.assertEqual(fps2, [p2, p3])
            self.assertEqual(fps3, [p3, p4])
            self.assertEqual(fps4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)


