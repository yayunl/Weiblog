from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from flask_babel import _
from datetime import  datetime
from guess_language import guess_language
from flask_babel import get_locale
from flask_login import current_user, login_required
# microblog level imports
from ..models import User, Post, Message, Notification, db
from ..translate import translate
# sub feature level imports
from .forms import EditProfileForm, PostForm, SearchForm, MessageForm
from . import bp


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale=str(get_locale())


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(
        request.form['text'],
        request.form['toLang']
    )})


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()

    if form.validate_on_submit():
        lang = guess_language(form.post.data)
        if lang == 'UNKNOWN' or len(lang) >5:
            lang = ''

        post = Post(body=form.post.data, author=current_user, language=lang)
        db.session.add(post)
        db.session.commit()
        flash("Posted your thought!")
        return redirect(url_for('core.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.idols_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)

    # pagination
    next_page_url, prev_page_url = url_for('core.index', page=posts.next_num) if posts.has_next else None, \
                                   url_for('core.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('core/index.html',
                           title='Home',
                           posts=posts.items,
                           form=form,
                           prev_page_url=prev_page_url, next_page_url=next_page_url,
                           next_what='Newer posts', prev_what='Older posts')


@bp.route('/user/<username>')
@login_required
def user_profile(username):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    user_query = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    posts = user_query.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    # pagination
    next_page_url, prev_page_url = url_for('core.explore', page=posts.next_num) if posts.has_next else None, \
                                   url_for('core.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('core/user_profile.html',
                           user=user_query,
                           posts=posts.items,
                           next_page_url=next_page_url, prev_page_url=prev_page_url,
                           next_what='Newer posts', prev_what='Older posts')


@bp.route('/edit', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfileForm()

    # if current_user.username != username:
    #     flash("You are not allowed to edit others' profile.")
    #     return redirect(url_for('edit_profile', username=current_user.username))

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash("Changes have been saved.")
        return redirect(url_for('core.user_profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('core/edit_profile.html', form=form, title='Edit Profile')


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()

    if not user or user == current_user:
        flash("Invalid request!")
        return redirect(url_for('core.index'))

    current_user.follow(user)
    db.session.commit()
    flash(f"You are following {username}!")
    return redirect(url_for('core.user_profile', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):

    user = User.query.filter_by(username=username).first()

    if not user or user == current_user:
        flash("Invalid request!")
        return redirect(url_for('core.index'))

    current_user.unfollow(user)
    db.session.commit()
    flash(f"You are not following {username}!")
    return redirect(url_for('core.user_profile', username=username))


@bp.route('/follower-idols/<username>/<type>')
@login_required
def follower_idols(username, type='follower'):
    usrq = User.query.filter_by(username=username).first()
    return render_template('core/follower_idols.html',
                           user=usrq,
                           type=type)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)

    next_page_url, prev_page_url = url_for('core.explore', page=posts.next_num) if posts.has_next else None, \
                                   url_for('core.explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('core/index.html',
                           title='Explore',
                           posts=posts.items,
                           next_page_url=next_page_url,prev_page_url=prev_page_url,
                           next_what='Newer posts', prev_what='Older posts')


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('core.explore'))

    # search
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page, current_app.config.get('POSTS_PER_PAGE'))

    # pagination
    next_page_url = url_for('core.search', q=g.search_form.q.data, page=page+1) if total > page * current_app.config.get('POSTS_PER_PAGE') else None
    prev_page_url = url_for('core.search', q=g.search_form.q.data, page=page-1) if page > 1 else None

    # return
    return render_template('search.html',
                           posts=posts,
                           next_page_url=next_page_url,prev_page_url=prev_page_url,
                           next_what='Newer posts', prev_what='Older posts')


@bp.route('/user/<username>/popup')
@login_required
def popup(username):
    """
    Response to Ajax request.
    :param username:
    :return:
    """
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('core/popup.html', user=user)


# Send messages
@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    """
    Send messages to a recipient.
    :param recipient:
    :return:
    """
    recipient = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(author=current_user,
                      recipient=recipient,
                      body=form.message.data)
        db.session.add(msg)

        # Update notification
        recipient.update_notification('unread_message_count', recipient.new_messages())
        db.session.commit()

        flash(_("Your message has been sent."))
        return redirect(url_for('core.user_profile', username=recipient.username))
    return render_template('core/send_message.html', title='Send Message',
                           form=form, recipient=recipient)

# View messages
@bp.route('/read_messages')
@login_required
def read_messages():
    current_user.last_message_read_time = datetime.utcnow()
    # update notification
    current_user.update_notification('unread_message_count', 0)
    db.session.commit()

    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate( page, current_app.config['POSTS_PER_PAGE'], False)

    next_url, prev_url = url_for('core.read_messages', page=messages.next_num) if messages.has_next else None, \
        url_for('core.read_messages', page=messages.prev_num) if messages.has_prev else None

    return render_template('core/read_messages.html',
                           posts=messages.items,
                           next_page_url=next_url, prev_page_url=prev_url,
                           next_what='Older messages', prev_what='Newer messages')


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp >= since).order_by(Notification.timestamp.asc())
    return jsonify([{'name': n.name, 'data': n.get_data(), 'timestamp': n.timestamp} for n in notifications])


# Export posts
@bp.route('/export_posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash(_('An export task is currently in progress.'))
    else:
        current_user.launch_task('export_posts', _('Exporting posts...'))
        db.session.commit()
    return redirect(url_for('core.user_profile', username=current_user.username))