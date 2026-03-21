from flask import Blueprint, render_template
from utils.helpers import login_required_v2

tools_bp = Blueprint('tools_bp', __name__)

@tools_bp.route('/')
@login_required_v2
def index():
    return render_template('cyber_tools.html')
