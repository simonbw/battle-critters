"""
Reset the server. Wipes the database and clears all the user files.
"""

import os
import shutil
import sqlite3
import sys
import time
import traceback
from flask import g

import database
import users

def reset_all():
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
				u = users.create_user("simon", "simon", True)
				for name in ["bob", "joe", "example"]:
					print name
					u = users.create_user(name, name)
			except:
				traceback.print_exc(file=sys.stdout)
				errored = True

			try:
				print "Creating default news posts."
				for title, content in [("First","Content of the first post"),("Second", "content of the second post")]:
					g.db.execute("INSERT INTO news (title,date,content) VALUES (?,?,?)", (title,time.time(),content))
					time.sleep(0.01)
				g.db.commit();
			except:
				traceback.print_exc(file=sys.stdout)
				errored = True

		if errored:
			raise Exception()

	except Exception as e:
		traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
	reset_all()
