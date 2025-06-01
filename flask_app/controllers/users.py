from flask import Blueprint, render_template, request, redirect, session, flash
from flask_app.models.user import User
from flask_app import bcrypt
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('users', __name__)

@bp.route('/login')
def login_page():
    if 'user' in session:
        return redirect('/dashboard')
    return render_template("loginRegister.html")

@bp.route('/registerUser', methods=['POST'])
def register():
    if not User.validate_user(request.form):
        return redirect('/login')
    
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "password": pw_hash
    }
    user_id = User.create_user(data)
    session['user'] = user_id
    return redirect('/dashboard')

@bp.route('/loginUser', methods=['POST'])
def login():
    data = { "email": request.form["email"] }
    user_in_db = User.get_user_by_email(data)
    if not user_in_db:
        flash("Invalid Email/Password", 'login')
        return redirect("/login")
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Invalid Email/Password", 'login')
        return redirect('/login')
    session['user'] = user_in_db.id
    return redirect("/dashboard")

@bp.route('/dashboard')
def dashboard():
    logger.debug("Accessing dashboard route")
    if 'user' not in session:
        logger.warning("No user in session, redirecting to 404")
        return redirect('/404Error')
    
    data = {
        'id': session['user']
    }
    logger.debug(f"Fetching user data for user_id: {data['id']}")
    logged = User.get_user_by_id(data)
    
    if not logged:
        logger.error(f"Failed to fetch user data for user_id: {data['id']}")
        flash("Error loading user data", "error")
        return redirect('/login')
    
    logger.debug(f"User data loaded successfully: {logged.first_name} {logged.last_name}")
    logger.debug(f"Number of pies loaded: {len(logged.pies)}")
    if logged.pies:
        logger.debug(f"First pie data: {logged.pies[0].__dict__ if logged.pies else 'No pies'}")
    
    return render_template("dashboard.html", logged=logged)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')