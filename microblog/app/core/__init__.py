from flask import Blueprint
bp = Blueprint('core', __name__, template_folder='templates')

from . import views