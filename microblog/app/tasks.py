from flask import current_app, render_template
from rq import get_current_job
import sys, time, json

from . import db, create_app
from .models import Task, User, Post
from .email import send_email

app = create_app()


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        # Use the meta to save the progress on fly
        job.meta['progress'] = progress
        job.save_meta()

        # Update the progress to database
        task = Task.query.get(job.get_id())
        task.user.update_notification('task_progress', #name
                                      {'task_id': job.get_id(),
                                       'progress': progress}) # data

        if progress >= 100:
            task.complete = True
        db.session.commit()


def export_posts(user_id):
    with app.app_context():
        try:
            # read posts from database and send email with data to user
            user = User.query.get(user_id)
            _set_task_progress(0)
            data = []
            i = 0
            total_post_count = user.posts.count()

            # Exporting process
            for post in user.posts.order_by(Post.timestamp.asc()):
                data.append({
                    'body': post.body,
                    'timestamp': post.timestamp.isoformat()+'Z'
                })
                time.sleep(5)
                i +=1
                # Update progress
                _set_task_progress(100*i//total_post_count)

                # send email
                subject='[Microblog]Your blog posts'
                sender=current_app.config['ADMIN_EMAIL']
                recipients=[user.email]
                text_body = render_template('email/export_posts.txt', user=user)
                html_body = render_template('email/export_posts.html', user=user)
                attachments  = [('posts.json',
                                 'application/json',
                                 json.dumps({'posts': data}, indent=4))]
            send_email(subject=subject,
                       sender=sender,
                       recipients=recipients,
                       text_body=text_body,
                       html_body=html_body,
                       attachments=attachments,
                       sync=True) # Use redis queue to send email

        except:
            # handle errors
           _set_task_progress(100)
           current_app.logger.error('Unhandled exception', exc_info=sys.exc_info())