from flask_mail import Message
from .extensions import mail
from threading import Thread
from flask import current_app


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body, attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        current_app.logger.info("Sent the sync email.")
        mail.send(msg)
    else:
        Thread(target=send_async_email,
               args=(current_app, msg)).start()