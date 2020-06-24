from app import create_app, db, cli
from app.models import User, Post, Notification, Message, Task


flask_app = create_app()
cli.register(flask_app)


@flask_app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post,
            'Message': Message, 'Notification': Notification, 'Task': Task}