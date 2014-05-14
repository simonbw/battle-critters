"""
Start the development server.
"""

print "\n====================\nMAIN IS LOADING \n====================\n"

import contextlib
import logging
import os
import sqlite3
import subprocess
import sys
import traceback
from flask import Flask, request, g, session, flash
from flask.ext.scss import Scss
from multiprocessing import Process
from py4j.java_gateway import JavaGateway

from battles import battles_app
from editor import editor_app
from feedback import feedback_app
from home import home_app
from login import login_app
from users import users_app, User
import battles
import database
import editor
import feedback
import home
import login
import users

####################################################
# Switch this for production vs development server #
PRODUCTION = True
####################################################

app = Flask(__name__)

# register blueprints
app.register_blueprint(battles_app, url_prefix = '/battles')
app.register_blueprint(editor_app, url_prefix = '/critters')
app.register_blueprint(home_app)
app.register_blueprint(login_app)
app.register_blueprint(feedback_app, url_prefix = '/feedback')
app.register_blueprint(users_app, url_prefix = '/users')

# configuration
DEBUG = False
SECRET_KEY = 'development key' #Used to keep client-side sessions secure.
app.config.from_object(__name__)

def start_java_server():
	"""Start the java server. This should be run in its own process."""
	cp = os.path.join('.', 'java','bin') + os.pathsep + os.path.join('.', 'java','lib','py4j0.8.jar')
	command = ["java", "-cp", cp, "battlecritters.Main"]
	print command
	subprocess.Popen(command, shell=False)
	print "Java server started"

@app.before_first_request
def before_first_request():
	"""Initialize everything"""

	print "initializing modules"
	for module in (battles, editor, home, login, users):
		try:
			module.init()
		except Exception as e:
			print str(e)

	print "compiling scss"
	app.scss = Scss(app, static_dir='static', asset_dir='.')
	app.scss.update_scss()

	print "creating java server"
	p = Process(target=start_java_server)
	p.daemon = True
	p.start()
	print "java server pid:", p.pid

	if not PRODUCTION:
		print "not in production mode"
		flash("not in production mode")

@app.before_request
def before_request():
	"""Called before the request is routed. Sets up the link to the database and java server."""

	# recompile the scss every request if not in production
	if not PRODUCTION:
		try:
			app.scss.update_scss()
		except Exception as e:
			flash(str(e))

	# link to the java server
	try:
		g.java_server = JavaGateway().entry_point
	except Exception:
		traceback.print_exc(file=sys.stdout)
	
	# prepare the database
	g.db = database.connect_db()

	# set global settings
	g.production = PRODUCTION

	# since User object is not serializable
	if ('username' in session):
		try:
			g.user = User.from_username(session['username'])
		except LookupError as e:
			login.logout()

@app.teardown_request
def teardown_request(exception):
	"""Close the database connection"""
	if 'db' in g :
		g.db.close()

@app.route('/reset')
def reset_page():
	try:
		from reset import reset_all
		reset_all()
		return "success"
	except Exception as e:
		return Markup(e)

# Start the server	
if __name__ == "__main__":	
	if not app.debug:
		log_file = 'log.txt'
		with open(log_file, 'w') as f:
			f.write("")
		file_handler = logging.FileHandler(log_file)
		file_handler.setLevel(logging.WARNING)
		app.logger.addHandler(file_handler)

	# This only gets set in debug mode I think...
	PRODUCTION = False

	# start the python app
	app.run(threaded=True, host="0.0.0.0")
