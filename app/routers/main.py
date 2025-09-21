from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return ""

@main_bp.route('/home')
def home():
    return render_template('main.html')
