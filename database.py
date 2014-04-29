"""
Run this file to setup the database
"""

import sqlite3
import contextlib
from flask import Flask, request, g, session

DATABASE = 'database.db'

def connect_db():
	"""Returns a connection to the database"""
	connection = sqlite3.connect(DATABASE)
	connection.row_factory = sqlite3.Row
	connection.text_factory = str
	return connection

def init_db(app):
	"""Creates and resets all the tables in the database."""
	print "Resetting database..."
	with contextlib.closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()
	print "done"


if __name__ == "__main__":
    from main import app
    init_db(app)