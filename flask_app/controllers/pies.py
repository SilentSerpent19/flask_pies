from flask import Blueprint, render_template, request, redirect, session, flash
from flask_app.models.pie import Pie
from flask_app.models.user import User
from flask_app import limiter

bp = Blueprint('pies', __name__)

@bp.route('/pie/new')
@limiter.limit("30 per minute")
def pie():
    if 'user' not in session:
        return redirect('/404Error')
    data = {
        'id': session['user']
    }
    logged = User.get_user_by_id(data)
    return render_template("createPie.html", logged=logged)

@bp.route('/pie/create', methods=['POST'])
@limiter.limit("15 per minute")
def form_pie():
    if 'user' not in session:
        return redirect('/404Error')
    
    if not Pie.validate_pie(request.form, session['user'], is_edit=False):
        flash("Please fix the errors in your pie submission", 'pieCreate')
        return redirect('/pie/new')
    
    data = {
        'name': request.form['name'],
        'filling': request.form['filling'],
        'crust': request.form['crust'],
        'user_id': session['user']
    }
    Pie.create_pie(data)
    flash("Pie created successfully!", 'success')
    return redirect('/dashboard')

@bp.route('/pie/view/<int:id>')
@limiter.limit("40 per minute")
def view_pie(id):
    if 'user' not in session:
        return redirect('/404Error')
    data = {
        'id': id
    }
    pie = Pie.get_pie_by_id(data)
    if not pie:
        return redirect('/404Error')
    vote_count = Pie.get_vote_count(id)
    user_voted = Pie.user_voted(session['user'], id)
    is_baker = (pie.user_id == session['user'])
    return render_template("viewPie.html", pie=pie, vote_count=vote_count, user_voted=user_voted, is_baker=is_baker)

@bp.route('/pie/edit/<int:id>')
@limiter.limit("30 per minute")
def edit_pie(id):
    if 'user' not in session:
        return redirect('/404Error')
    data = {
        'id': id
    }
    currentPie = Pie.get_pie_by_id(data)
    if not currentPie or not session['user'] == currentPie.user_id:
        return redirect('/404Error')
    return render_template("editPie.html", pie=currentPie)

@bp.route('/pie/update/<int:id>', methods=['POST'])
@limiter.limit("15 per minute")
def updating(id):
    if 'user' not in session:
        return redirect('/404Error')
    if not Pie.validate_pie(request.form, session['user'], is_edit=True, pie_id=id):
        flash("All fields must be complete", 'updatePie')
        return redirect(request.referrer)

    data = {
        'id': id,
        'name': request.form['name'],
        'filling': request.form['filling'],
        'crust': request.form['crust'],
        'user_id': session['user']
    }

    Pie.update_pie(data)
    flash("Pie updated successfully!", 'success')
    return redirect('/dashboard')

@bp.route('/pie/delete/<int:id>')
@limiter.limit("15 per minute")
def delete(id):
    data = {
        'id': id
    }
    pie = Pie.get_pie_by_id(data)
    if not pie or not session['user'] == pie.user_id:
        return redirect('/404Error')

    Pie.delete_pie(data)
    flash("Pie deleted successfully!", 'success')
    return redirect(request.referrer)

@bp.route('/404Error')
@limiter.limit("40 per minute")
def error():
    return render_template("404Error.html")

@bp.route('/pies')
@limiter.limit("40 per minute")
def all_pies():
    if 'user' not in session:
        return redirect('/404Error')
    pies = Pie.all_pies()
    user_votes = set()
    if pies:
        user_votes = {pie.id for pie in pies if Pie.user_voted(session['user'], pie.id)}
    return render_template('allPies.html', pies=pies, user_votes=user_votes, user_id=session['user'])

@bp.route('/pie/vote/<int:pie_id>', methods=['POST'])
@limiter.limit("25 per minute")
def vote_pie(pie_id):
    if 'user' not in session:
        return redirect('/404Error')
    Pie.cast_vote(session['user'], pie_id)
    return redirect(request.referrer or '/pies')

@bp.route('/pie/unvote/<int:pie_id>', methods=['POST'])
@limiter.limit("25 per minute")
def unvote_pie(pie_id):
    if 'user' not in session:
        return redirect('/404Error')
    Pie.remove_vote(session['user'], pie_id)
    return redirect(request.referrer or '/pies')







