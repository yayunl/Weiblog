from ..email import send_email
from flask import render_template, current_app


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    subject= '[Micro-blog] Reset your password!'
    sender = current_app.config.get('ADMIN_EMAIL')
    recipients = [user.email]
    text = render_template('email/reset_password_txt.txt',
                           user=user,
                           token=token)
    html = render_template('email/reset_password_htm.html',
                           user=user,
                           token=token)

    send_email(subject=subject,
               sender=sender,
               recipients=recipients,
               text_body=text,
               html_body=html)