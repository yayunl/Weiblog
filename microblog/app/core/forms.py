from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_babel import lazy_gettext as _l
from flask import request


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Edit'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Post your thoughts'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Post'))


class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args

        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False

        super(SearchForm, self).__init__(*args, **kwargs)

