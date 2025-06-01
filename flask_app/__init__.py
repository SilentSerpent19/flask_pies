from flask import Flask, render_template, request, redirect, session, flash
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import logging
from logging.handlers import RotatingFileHandler

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "shhhhhh"

# Set up logging
if not os.path.exists('logs'):
    os.mkdir('logs')

# Configure file handler
file_handler = RotatingFileHandler('logs/flask_app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

# Set console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
console_handler.setLevel(logging.DEBUG)
app.logger.addHandler(console_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('Flask application startup')

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize bcrypt
bcrypt = Bcrypt(app)

# Set database configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '@00#we4/')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DATABASE', 'pies')

# Import and register blueprints after app initialization
from flask_app.controllers import users, pies
app.register_blueprint(users.bp)
app.register_blueprint(pies.bp)

@app.route('/')
def index():
    return redirect('/login')

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('rate_limit.html', error=str(e)), 429

@app.errorhandler(404)
def page_not_found(e):
    # If the request is for a static file or API endpoint, return JSON
    if request.path.startswith('/static/') or request.path.startswith('/api/'):
        return {'error': 'Not found'}, 404
    # For regular pages, render the 404 template
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)