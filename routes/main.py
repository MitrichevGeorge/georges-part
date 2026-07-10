from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template("index.html")

@main_bp.route('/map')
def map_view():
    return render_template("map.html")

@main_bp.route('/streetview')
def streetview_view():
    return render_template("streetview.html")