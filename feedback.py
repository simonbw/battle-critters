"""
Manages user submitted feedback.
"""

import time

from flask import Blueprint, g, render_template, request, redirect, session, url_for, flash

import util
from password import hash_password

feedback_app = Blueprint('feedback_app', __name__, template_folder='templates')


def init():
	"""Initialize the module"""
	pass


@feedback_app.route('/', methods=['GET', 'POST'])
def feedback_page():
	if request.method == 'POST':
		if 'content' in request.form:
			try:
				query = "INSERT INTO feedback (content) VALUES ?"
				g.db.execute(query, (request.form['content'],))
			except Exception as e:
				flash("<strong>Error submitting feedback:</strong>" + e)
		return redirect(url_for('home_app.home_page'))
	elif request.method == 'GET':
		return render_template('feedback.html')

@feedback_app.route('/view', methods=['GET'])
@util.admin_required
def view_feedback():
	rows = g.db.execute("SELECT * FROM feedback ORDER BY date DESC LIMIT 100").fetchall()
	for row in rows:
		row['date'] = util.format_date(row['date'])
	return render_template('view_feedback.html', feedback=rows)