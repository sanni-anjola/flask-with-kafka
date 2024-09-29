from flask import Blueprint


admin_bp = Blueprint('admin_bp', __name__, url_prefix='/api/v1/admin')

@admin_bp.route('/')
def index():
    return "This is an example app"