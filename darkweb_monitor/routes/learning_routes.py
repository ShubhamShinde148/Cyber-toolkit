from flask import Blueprint, render_template
from utils.helpers import login_required_v2

learning_bp = Blueprint('learning_bp', __name__)

@learning_bp.route('/')
@login_required_v2
def index():
    return render_template('learning_mode.html')
