#!/usr/bin/env python
"""
Reset the server. Wipes the database and clears all the user files.
"""

import os
import ranking
import shutil
import sqlite3
import sys
import time
import traceback
from flask import g

import database
import users

def reset_all():
	import editor
	import main
	from main import app
	database.init_db(app)

	try:
		errored = False
		with app.app_context():
			g.db = database.connect_db()
			g.db.row_factory = sqlite3.Row

			try:
				critter_dir = os.path.join('.', 'java', 'bin', 'battlecritters', 'critters')
				print "resetting critter directory:", critter_dir
				try:
					shutil.rmtree(critter_dir)
				except:
					print "not found"
				os.mkdir(critter_dir)
			except:
				traceback.print_exc(file=sys.stdout)
				errored = True

			try:
				critter_dir = os.path.join('.', 'java', 'temp_critters')
				print "resetting critter temp directory:", critter_dir
				try:
					shutil.rmtree(critter_dir)
				except:
					print "not found"
				os.mkdir(critter_dir)
			except:
				traceback.print_exc(file=sys.stdout)
				errored = True

			try:
				print "Creating default users..."
				users.create_user("admin", "admin", True)
				users.create_user("example", "example", False)
			except:
				traceback.print_exc(file=sys.stdout)
				errored = True

			try:
				print "Creating default critters..."
				example = users.User.from_username('example')

				path = os.path.join('static', 'examplecritters')
				for filename in os.listdir(path):
					with open(os.path.join(path, filename), 'r') as f:
						editor.create_file(example, filename[:-5], f.read())
			except:
				traceback.print_exc(file=sys.stdout)
				errored = True

			try:
				print "Creating default news posts."
				for title, content in [("First","Content of the first post"),("Second", "content of the second post")]:
					g.db.execute("INSERT INTO news (title,date,content) VALUES (?,?,?)", (title,time.time(),content))
					time.sleep(0.01)
			except:
				traceback.print_exc(file=sys.stdout)
				errored = True

			g.db.commit();
		if errored:
			raise Exception()

	except Exception as e:
		traceback.print_exc(file=sys.stdout)

def reset_scores():
	import editor
	import main
	from main import app

	with app.app_context():
		print "resetting scores"
		g.db = database.connect_db()
		g.db.row_factory = sqlite3.Row
		g.db.execute("UPDATE critters SET score = ?", (ranking.DEFAULT_SCORE,))
		g.db.commit()

if __name__ == "__main__":
	args = {a for a in sys.argv}
	if '-s' in args or '--scores' in args:
		reset_scores()
	if '-a' in args or '--all' in args:
		reset_all()
	else:
		print "no args given"