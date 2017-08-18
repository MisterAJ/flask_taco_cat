from flask import Flask, g, render_template, flash, redirect, url_for
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user,
                             logout_user, login_required, current_user)

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'youdontknowmysecretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.db
    g.db.get_conn()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        models.User.create_user(
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Email is incompatible", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You are logged in", "success")
                return redirect(url_for('index'))
            else:
                flash("Password does not match", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


@app.route('/taco', methods=('GET','POST'))
@login_required
def taco():
    form = forms.TacoForm()
    if form.validate_on_submit():
        models.Taco.create(user=g.user._get_current_object(),
                           protein=form.protein.data,
                           shell=form.shell.data,
                           cheese=form.cheese.data,
                           extras=form.extras.data.strip()
                           )
        flash("Your taco has been added!!", "success")
        return redirect(url_for('index'))
    return render_template('taco.html', form=form)


@app.route('/')
def index():
    tacos = models.Taco.select().limit(10)
    if len(tacos) < 1:
        flash('no tacos yet')
        return render_template('index.html', tacos=tacos)
    return render_template('index.html', tacos=tacos)


if __name__ == '__main__':
    models.initialize()
    try:
        with models.db.transaction():
            models.User.create_user(
                email='billy@example.com',
                password='password'
            )
            user = models.User.select().get()
            models.Taco.create(
                user=user,
                protein='chicken',
                shell='flour',
                cheese=False,
                extras='Gimme some guac.'
            )
    except ValueError:
        pass
