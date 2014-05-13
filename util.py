"""
Assorted Utility functions and classes for doing all sorts of things. Does not depend on any of my files.
"""

from flask import jsonify, session
from functools import wraps
import datetime
import string
import sys
import time
import traceback


def format_date(seconds):
	"""Return a date/time formatted nicely."""
	now = datetime.datetime.today()
	date = datetime.datetime.fromtimestamp(seconds)
	if date.date() == now.date():
		return date.strftime('%I:%M %p')
	return date.strftime('%a %H:%M %p')

def json_service(f):
	"""Wraps a function that returns a json object."""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		try:
			results = f(*args, **kwargs)
			if results == None:
				results = {}
			if not isinstance(results, dict):
				results = {'result': results}
			results['success'] = True
			return jsonify(results)
		except Exception as e:
			return jsonify({'success': False, 'error': str(e)})
	return decorated_function

def error_checked(f):
	"""Prints stack trace when the method fails."""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			raise e
	return decorated_function

def login_required(f):
	"""Requires a user to be logged in to view a page."""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'username' not in session:
			return redirect(url_for('login_app.login', next=request.url))
		return f(*args, **kwargs)
	return decorated_function

def require_user(username, allow_admin=True):
	"""Throws a 403 if the logged in user is not the user specified or an admin."""
	if 'username' not in session:
		abort(403)
	if session['username'] != username and not (allow_admin and g.user.admin):
		abort(403)

def admin_required(f):
	"""Requires a user to be admin to view a page otherwise returns a 403."""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'user' not in g or not g.user.admin:
			abort(403)
		return f(*args, **kwargs)
	return decorated_function