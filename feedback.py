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
				query = "INSERT INTO feedback (content, date) VALUES (?, ?)"
				g.db.execute(query, (request.form['content'], time.time()))
				g.db.commit()
			except Exception as e:
				flash("<strong>Error submitting feedback:</strong>" + str(e))
		return redirect(url_for('home_app.home_page'))
	elif request.method == 'GET':
		return render_template('feedback.html')

@feedback_app.route('/view', methods=['GET'])
@util.admin_required
@util.error_checked
def view_feedback():
	rows = g.db.execute("SELECT * FROM feedback ORDER BY date DESC LIMIT 100").fetchall()
	feedback = [{'date': util.format_date(row['date']), 'content': row['content'], 'id': row['id']} for row in rows]
	return render_template('view_feedback.html', feedback=feedback)
