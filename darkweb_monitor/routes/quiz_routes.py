from flask import Blueprint, render_template

quiz_bp = Blueprint('quiz_bp', __name__)

@quiz_bp.route('/')
def quiz_hub():
    return "Quiz V2 Engine Hub"
