"""
Contains the User model as well as the pages for creating and displaying users.
"""

import os
import re
import shutil
import sqlite3

from flask import Flask, g, redirect, request, session, render_template, Blueprint, url_for, Markup, abort, flash

from battles import Battle
from editor import Critter
from password import hash_password
import battles
import util
import login

users_app = Blueprint('users_app', __name__, template_folder='templates')

# the regex for testing if a username is valid
USERNAME_TEST = re.compile(r'[A-Z|a-z][\w]*')

class User:
	"""A model for a user. Handles database comunication. To load a User, use one of the static methods."""
	@staticmethod
	def from_username(username):
		"""Load a User from the database based on username"""
		row = g.db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
		if row is None:
			raise LookupError("User not found: " + username)
		return User(row)

	@staticmethod
	def from_id(id):
		"""Load a User from the database based on id"""
		row = g.db.execute("SELECT * FROM users WHERE id=?", (id,)).fetchone()
		if row is None:
			raise LookupError("User not found: " + str(id))
		return User(row)

	def __init__(self, row):
		"""Initialize a User from a database row. You should probably look at the static constructors."""
		if not (row['id'] and row['username'] and row['password']):
			raise Exception("improper constructor")

		self.id = row['id']
		self.username = row['username']
		self.admin = bool(row['admin'])
		self.password = row['password']


	def get_url(self):
		"""Return the url for the user's page."""
		return url_for('users_app.show_user', username=self.username)

	def get_link(self, text=None):
		"""Return an HTML snippet with a link to the userpage. If text is none, defaults to the username."""
		admin = (" admin") if self.admin else ""
		if text is None:
			text = self.username
		return Markup("<a href='{url}' class='username{admin}'>{text}</a>".format(
					url=self.get_url(),
					text=text,
					admin=admin))

	def get_critters(self):
		"""Return a list of Critters owned by this User."""
		rows = g.db.execute('SELECT * FROM critters WHERE owner_id=?;', (self.id,)).fetchall()
		critters = map(Critter, rows)
		return critters

	def get_critter(self, name):
		"""Return the Critter owned by this User with a specific name"""
		row = g.db.execute('SELECT * FROM critters WHERE owner_id=? AND name=?;', (self.id,name)).fetchone()
		if row is None:
			raise LookupError("Cannot find " + self.username + "." + name)
		return Critter(row)

	def get_battles(self, limit=20):
		"""Return a list of recent battles this user's critters have been in."""
		limit = int(limit)
		rows = g.db.execute("SELECT DISTINCT battles.id FROM battles, battle_critters, critters \
			WHERE battles.id=battle_critters.battle_id \
			AND battle_critters.critter_id=critters.id \
			AND critters.owner_id=? \
			ORDER BY battles.creation_time DESC \
			LIMIT ?;", (self.id, limit)).fetchall()

		return [Battle.from_id(row[0]) for row in rows]

	def __str__(self):
		return "<User: {0},{1}>".format(self.id, self.username)

	def __eq__(self, other):
		"""Check if users are the same. Based on id."""
		if isinstance(other, self.__class__):
			return self.id == other.id
		else:
			return False

@users_app.route('/')
def list_users():
	"""A page listing all users."""
	user_list = g.db.execute("SELECT * FROM users ORDER BY admin, username").fetchall()
	user_list = map(User, user_list)
	return render_template('users.html', user_list=user_list)

@users_app.route('/<username>')
def show_user(username):
	"""Display a user's page."""
	try:
		u = User.from_username(username)
		return render_template('user.html', user=u)
	except LookupError as e:
		abort(404)

@users_app.route('/new', methods = ['GET', 'POST'])
def new_user():
	"""The page for creating a new user."""
	if request.method == 'POST':
		try:
			if request.form['password'] != request.form['password2']:
				raise Exception("Passwords do not match")
			username = request.form['username']
			raw_password = request.form['password']
			create_user(username, raw_password)
			return redirect(url_for('login_app.login_page'))
		except Exception as e:
			flash(Markup(str(e)))
			return render_template('new_user.html')
	else:
		return render_template('new_user.html')

def create_user(username, raw_password, admin=False):
	"""Try to create a User."""
	try:
		if (not USERNAME_TEST.match(username)):
			raise Exception("Invalid Username")
		password = hash_password(raw_password, username)
		g.db.execute('INSERT INTO users (username, password, admin) VALUES (?,?,?);', (username, password, int(admin)))
		g.db.commit()

		critter_dir = os.path.join('.', 'java', 'bin', 'battlecritters', 'critters', username)
		os.mkdir(critter_dir)

		return User.from_username(username)
	except sqlite3.IntegrityError as e:
		raise Exception("username <em>" + username + "</em> is taken")
	except sqlite3.OperationalError as e:
		raise e
	except sqlite3.DatabaseError as e:
		raise e

def delete_user(username):
	"""Delete a user and all owned critters."""
	user = User.from_username(username)
	try:
		g.db.execute('DELETE FROM users WHERE username=?', (username,))
		g.db.commit()
	except Exception:
		pass
	try:
		g.db.execute('DELETE FROM critters WHERE user_id=?', (user.id,))
	except Exception:
		pass
	try:
		critter_dir = os.path.join('.', 'java', 'bin', 'critters', username)
		shutil.rmtree(critter_dir)
	except Exception:
		pass