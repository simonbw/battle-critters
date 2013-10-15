"""
Display the home page. Also does news stuff and other static pages. For now.
"""

import time
import traceback

from flask import Blueprint, g, render_template, request, redirect, session, url_for, Markup

home_app = Blueprint('home_app', __name__, template_folder='templates')

@home_app.route('/')
@home_app.route('/home')
@home_app.route('/index')
def home_page():
	"""Display the homepage. Different for logged in users."""
	try:
		if 'username' in session:
			max_news = 2
			return render_template('user_home.html', max_news=max_news)
		else:
			return render_template('guest_home.html')
	except Exception as e:
		traceback.print_exc()
		return Markup("ERROR: " + repr(e))

@home_app.route('/news', methods=["GET", "POST", "PUT"])
def news():
	try:
		if request.method == "GET":
			if reqest.args['max']:
				result = 2
			else:
				offset = int(request.args['page'])
				return render_template('news_format.html', articles=g.db.execute("SELECT * FROM news ORDER BY date DESC LIMIT 1 OFFSET ?", (offset,)).fetchall())
		elif request.method == "POST" or request.method == "PUT":
			title = request.form['title']
			content = request.form['content']
			g.db.execute("INSERT INTO news (title,date,content) VALUES (?,?,?)", (title,time.time(),content))
			g.db.commit()
			return "success"	
	except Exception as e:
		traceback.print_exc()
		return Markup(e)



#-------- STATIC PAGES --------#
@home_app.route('/FAQ')
def faq_page():
	return render_template('info/faq.html')

@home_app.route('/rules')
def rules_page():
	return render_template('info/rules.html')

@home_app.route('/about_us')
def about_us_page():
	return render_template('info/about_us.html')
