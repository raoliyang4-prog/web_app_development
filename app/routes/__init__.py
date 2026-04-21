from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
event_bp = Blueprint('event', __name__)
registration_bp = Blueprint('registration', __name__)

from . import auth, event, registration

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(registration_bp)
