"""
Controls the login/logout pages.
"""

from flask import Blueprint, g, render_template, request, redirect, session, url_for, flash

import users
from password import hash_password

login_app = Blueprint('login_app', __name__, template_folder='templates')


def init():
	"""Initialize the module"""
	global User
	User = users.User


@login_app.route('/login', methods=['GET', 'POST'])
def login_page():
	"""Display the login page"""
	if request.method == 'POST':
		try:
			g.user = User.from_username(request.form['username'])
			if g.user.password != hash_password(request.form['password'], g.user.username):
				raise Exception("Incorrect password")
			session['username'] = g.user.username
			return redirect(url_for('home_app.home_page'))
		except Exception as e:
			# make sure still logged out
			session.pop('username', None)
			if ('user' in g):
				del g.user
			flash(str(e))
			return render_template('login.html')
	elif 'username' in session:
		flash("already logged in as " + g.user.username)
		return redirect(url_for('home_page'))
	else:
		return render_template('login.html')

@login_app.route('/logout')
def logout():
	"""Log the user out and redirect to the home page."""
	session.pop('username', None)
	if ('user' in g):
		del g.user
	return redirect(url_for('home_app.home_page'))

