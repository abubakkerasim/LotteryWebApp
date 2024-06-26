# IMPORTS
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_login import current_user,LoginManager
from flask_talisman import Talisman
import logging

def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                logging.warning('SECURITY - Unauthorised Access Attempted [%s, %s, %s ,%s]',current_user.id ,current_user.email, current_user.role, request.remote_addr)
                return render_template('403.html')
            return f(*args, **kwargs)
        return wrapped
    return wrapper



# CONFIG
app = Flask(__name__)
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lf41H4iAAAAALCDw0esznqOX1-uxAKABhCYQ51_'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lf41H4iAAAAALw_t1vVYYcr9fUvBkqR7yjZqCwN'

# initialise database
db = SQLAlchemy(app)

#added security headers
csp = {
    'default-src': ['\'self\'',
                    'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.2/css/bulma.min.css'],
    'frame-src': ['\'self\'',
                  'https://www.google.com/recaptcha/',
                  'https://recaptcha.google.com/recaptcha/'],
    'script-src': ['\'self\'',
                   '\'unsafe-inline\'',
                   'https://www.google.com/recaptcha/',
                   'https://www.gstatic.com/recaptcha/']
}

talisman = Talisman(app, content_security_policy=csp)

# HOME PAGE VIEW
@app.route('/')
def index():
    return render_template('main/index.html')

@app.errorhandler(400)
def internal_error(error):
    return render_template('400.html'), 400

@app.errorhandler(403)
def internal_error(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(503)
def internal_error(error):
    return render_template('503.html'), 503

# BLUEPRINTS
# import blueprints
from users.views import users_blueprint
from admin.views import admin_blueprint
from lottery.views import lottery_blueprint
#
# # register blueprints with app
app.register_blueprint(users_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(lottery_blueprint)

login_manager = LoginManager()
login_manager.login_view ='users.login'
login_manager.init_app(app)

from models import User
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class SecurityFilter(logging.Filter):
    def filter(self, record):
        return 'SECURITY' in record.getMessage()

#logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('lottery.log', 'a')
file_handler.setLevel(logging.WARNING)
file_handler.addFilter(SecurityFilter())
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

if __name__ == "__main__":
    app.run()
