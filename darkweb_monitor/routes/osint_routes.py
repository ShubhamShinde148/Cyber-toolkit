from flask import Blueprint, render_template

osint_bp = Blueprint('osint_bp', __name__)

@osint_bp.route('/')
def osint_hub():
    return "OSINT V2 Engine Hub"
