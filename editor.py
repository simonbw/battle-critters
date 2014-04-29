"""
Handles the model, as well as pages for editing and viewing, of critter code.
"""

import os
import re
import string
import subprocess
import sys
import time
import traceback
import zlib

import sqlite3
from flask import Flask, g, redirect, request, session, render_template, Blueprint, url_for, Markup, abort, jsonify

import users
import ranking

JAVA_KEYWORDS = ('abstract', 'continue', 'for', 'new', 'switch', 'assert', 'default', 'goto', 'package', 'synchronized', 'boolean', 'do', 'if', 'private', 'this','break', 'double', 'implements', 'protected', 'throw', 'byte', 'else', 'import', 'public', 'throws', 'case', 'enum', 'instanceof', 'return', 'transient', 'catch', 'extends', 'int', 'short', 'try','char', 'final', 'interface', 'static', 'void', 'class', 'finally', 'long', 'strictfp', 'volatile','const', 'float', 'native', 'super', 'while')
JAVA_LETTERS = string.ascii_letters
JAVA_DIGITS = string.digits
JAVA_LETTERS_OR_DIGITS = JAVA_LETTERS + JAVA_DIGITS
MAX_CLASS_NAME_LENGTH = 128
COMPRESSION_LEVEL = 1
DEFAULT_CONTENT = ""
with open(os.path.join('static', 'default_critter.java')) as f:
	DEFAULT_CONTENT = f.read()

editor_app = Blueprint('editor_app', __name__, template_folder='templates')

class Critter():
	"""A model for a Critter. Handles database comunication. To load a Critter, use one of the static methods."""
	@staticmethod
	def from_name(filename, owner=None, owner_id=None, owner_name=None, fail_silent=False):
		"""Load a Critter from an owner and filename"""
		if owner_id == None:
			if owner == None:
				owner = users.User.from_username(owner_name)
			owner_id = owner.id

		row = g.db.execute("SELECT * FROM critters WHERE owner_id=? AND name=?", (owner_id, filename)).fetchone()
		if row is None:
			if fail_silent:
				return None
			else:
				raise LookupError("Critter not found: " + filename)
		return Critter(row)

	@staticmethod
	def from_id(id):
		"""Load a critter from id"""
		row = g.db.execute("SELECT * FROM critters WHERE id=?", (id,)).fetchone()
		if row is None:
			raise LookupError("Critter not found: " + str(id))
		return Critter(row)
	
	def __init__(self, row):
		"""Create a new critter from a database row"""
		self.id = row['id']
		self.name = row['name']
		if ('content' in row):
			self._content = zlib.decompress(row['content'])
		else:
			self._content = None
		self.owner_id = row['owner_id']
		self._owner = None
		self.creation_time = row['creation_time']
		self.last_save_time = row['last_save_time']
		self.score = row['score']

	@property
	def owner(self):
		"""Get the owner of this Critter"""
		if self._owner == None:
			self._owner = users.User.from_id(self.owner_id)
		return self._owner
	
	@owner.setter
	def owner(self, value):
		self._owner = value

	@property
	def content(self):
		"""Lazy load the content of this Critter"""
		if self._content == None:
			self._content = zlib.decompress(g.db.execute("SELECT content FROM critters WHERE id=?", (self.id,)).fetchone()['content'])
		return self._content

	@content.setter
	def content(self, value):
		self._content = value

	def get_all_battles(self):
		"""Return the list of battles this critter been in"""
		return map(battles.Battle.from_id, [row.id for row in g.db.execute("SELECT battle_id FROM battle_critters WHERE critter_id = ?", (self.id,)).fetchall()])

	def get_winning_battles(self):
		"""Return the list of battles this critter has won"""
		return map(battles.Battle.from_id, [row.id for row in g.db.execute("SELECT battle_id FROM battle_critters WHERE critter_id = ? AND winner = 1", (self.id,)).fetchall()])
	
	def get_losing_battles(self):
		"""Return the list of battles this critter has not won"""
		return map(battles.Battle.from_id, [row.id for row in g.db.execute("SELECT battle_id FROM battle_critters WHERE critter_id = ? AND winner = 0", (self.id,)).fetchall()])

	def get_url(self, action="view"):
		if action == 'view':
			return url_for('editor_app.view_file', owner=self.owner.username, filename=self.name)
		elif action == 'edit':
			return url_for('editor_app.view_file', owner=self.owner.username, filename=self.name)
		elif action == 'save':
			return url_for('editor_app.save_file', owner=self.owner.username, filename=self.name)
		elif action == 'compile':
			return url_for('editor_app.compile_file', owner=self.owner.username, filename=self.name)
		else:
			raise Exception("Unknown Action: " + action)

	def get_link(self, action='view', text=None):
		"""Return an HTML snippet with a link to the userpage. If text is none, defaults to 'ownername.name' ."""
		url = self.get_url(action)
		text = text if text else self.owner.username + '.' + self.name
		return Markup("<a href='{url}' class='crittername'>{text}</a>".format(url=url,text=text))

	def save(self):
		"""Save the current content of the critter in the database."""
		current_time = time.time()
		zcontent = zlib.compress(self.content, COMPRESSION_LEVEL)
		g.db.execute("UPDATE critters SET content=?, last_save_time=? WHERE name = ? AND owner_id = ?;", (
					zcontent, current_time, self.name, self.owner_id))
		g.db.commit()
		return current_time

	def compile(self):
		"""Compile the critter."""
		temp_name = os.path.join('.', 'java','temp_critters', self.name + '.java')
		content = process_file(self.content, self.owner.username, self.name)
		with open(temp_name, 'w') as f:
			f.write(content)
		command = "javac -cp {cp} -d {d} {filename}".format(
			cp=os.path.join('.', 'java','bin'),
			d=os.path.join('.', 'java', 'bin'),
			filename=temp_name)
		try:
			subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
			# save stuff
			return "success"
		except subprocess.CalledProcessError as e:
			return Markup(format_compiler_output(e.output))


	def reload(self):
		"""Reload all the data from this critter out of the database.""" 
		row = g.db.execute("SELECT * FROM critters WHERE owner=? AND name=?", (owner_id, filename)).fetchone()
		if row is None:
			raise LookupError("Critter not found: " + filename)
		self.__init__(row)

	def __str__(self):
		return "<Critter: {0},{1},{2}>".format(self.id, self.name, self.owner)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.id == other.id
		else:
			return False

@editor_app.route('/')
def critter_list_page():
	rows = g.db.execute('SELECT * FROM critters').fetchall()
	critters = map(Critter, rows)
	return render_template('list_all_critters.html', critters=critters)

@editor_app.route('/json')
def get_critters_json():
	"""Returns a JSON object containing a map of critter id to information such as name, owner_name, and owner_id."""
	# TODO: PLEASE REMOVE THIS. THIS IS JUST TO SIMULATE LATENCY
	time.sleep(0.1)
	# TODO: PLEASE REMOVE THIS. THIS IS JUST TO SIMULATE LATENCY
	
	r = {}
	for critter_id in request.args.getlist('ids[]'):
		c = Critter.from_id(critter_id)
		data = {}
		data['name'] = c.name
		data['owner_name'] = c.owner.username
		data['owner_id'] = c.owner.id
		r[c.id] = data
	return jsonify(r)

@editor_app.route('/get_ids/user')
def get_user_critter_ids():
	"""Return a JSON list of critter ids"""
	try:
		limit = request.args['limit']
		print "limit", limit
		owner_id = g.user.id
		query = "SELECT id FROM critters WHERE owner_id=? ORDER BY id LIMIT ?"
		rows = g.db.execute(query, (owner_id,limit)).fetchall()
		ids = [row['id'] for row in rows]
		return jsonify({'ids': ids})
	except Exception as e:
		print e
		return "error"

@editor_app.route('/get_ids/random')
def get_random_critter_ids():
	"""Return a JSON list of critter ids"""
	try:
		limit = request.args['limit']
		owner_id = g.user.id
		rows = g.db.execute("SELECT id FROM critters ORDER BY RANDOM() LIMIT ?", (limit,)).fetchall()
		ids = [row['id'] for row in rows]
		return jsonify({'ids': ids})
	except Exception as e:
		print e
		return "error"

@editor_app.route('/get')
def get_critter_list():
	"""Page that lists all critters. Can specify an owner."""
	if request.args['username']:
		u = users.User.from_username(request.args['username'])
		rows = g.db.execute('SELECT * FROM critters WHERE owner_id=?',(u.id,)).fetchall()
	else:
		rows = g.db.execute('SELECT * FROM critters').fetchall()
	critters = map(Critter, rows)
	delete_buttons = bool(request.args['delete_buttons'])
	result = Markup("")
	for critter in critters:
		result += Markup('<li>') + critter.get_link()
		if delete_buttons:
			result += Markup('\n<button class="deletebutton" onclick="delete_file(\'' + critter.name + '\')">Delete</button>') 
		result += Markup('</li>')
	return result

@editor_app.route('/<owner>/')
def list_user_files(owner):
	owner = users.User.from_username(owner)
	rows = g.db.execute('SELECT * FROM critters WHERE owner_id=?;', (owner.id,)).fetchall()
	critters = map(Critter, rows)
	return render_template('list_user_critters.html', critters=critters, owner=owner)

@editor_app.route('/<owner>/<filename>')
def view_file(owner, filename):
	critter = Critter.from_name(filename, owner_name=owner)
	return render_template('edit_critter.html', critter=critter)

@editor_app.route('/<owner>/<filename>', methods=['PUT', 'POST'])
def save_file(owner, filename):
	if (g.user.username != owner and not g.user.admin):
		raise Exception("You don't have permission to do that")

	try:
		critter = Critter.from_name(filename, owner_name=owner)
		critter.content = request.form['content']
		critter.save();
		return 'success'
	except Exception as e:
		return Markup("ERROR: " + str(e))

@editor_app.route('/<owner>/<filename>', methods=['DELETE'])
def delete_file(owner, filename):
	try:
		owner_id = users.User.from_username(owner).id
		print "deleting critter: " + filename + ", " + str(owner_id)
		# make sure it exists
		Critter.from_name(filename, owner_id=owner_id, fail_silent=False)
		
		try:
			path = os.path.join('.', 'java', 'bin', 'critters', owner, filename + '.class')
			os.remove(path)
		except EnvironmentError as e:
			pass

		g.db.execute("DELETE FROM critters WHERE name = ? AND owner_id = ?;", (filename, owner_id))
		g.db.commit()

		return 'success'
	except Exception as e:
		return Markup("ERROR: " + str(e))

@editor_app.route('/<owner>/<filename>/compile', methods=["GET","POST"])
def compile_file(owner, filename):
	"""This is sketchy if multiple files are being compiled at once.
	Compile a file. User must be the owner of the critter or an admin. Returns 'success', else returns compiler error message."""
	if (g.user.username != owner and not g.user.admin):
		raise Exception("You don't have permission to do that")
	critter = Critter.from_name(filename, owner_name=owner)
	return critter.compile()

@editor_app.route('/<owner>/<filename>/new', methods=["POST", "PUT"])
def new_file(owner, filename):
	"""Create a new file."""
	if (g.user.username != owner and not g.user.admin):
		raise Exception("You don't have permission to do that")
	try:
		if not check_filename(filename):
			raise Exception("Invalid Class Name")
		if (g.user.username != owner and not g.user.admin):
			raise Exception("You don't have permission to do that")

		owner = users.User.from_username(owner)
		
		if request.form.get("content") is not None:
			content = request.form['content']
		else:
			content = None
		create_file(owner, filename, content)
		return "success"
	except Exception as e:
		traceback.print_exc(file=sys.stdout)
		return Markup("ERROR: " + str(e))

def create_file(owner, filename, content=None):
	"""Actually create a new critter"""
	current_time = time.time()
	print "creating new critter: " + filename + ", owner id: " + str(owner.id)
	if content == None:
		content = DEFAULT_CONTENT.replace('{name}', filename)

	content = zlib.compress(content, COMPRESSION_LEVEL)

	critter = Critter.from_name(filename, owner_id=owner.id, fail_silent=True)
	if critter != None:
		raise Exception("That Critter already exists")
	query = "INSERT INTO critters (creation_time, last_save_time, name, owner_id, content, score) VALUES (?, ?, ?, ?, ?, ?)"
	g.db.execute(query, (current_time, current_time, filename, owner.id, content, ranking.DEFAULT_SCORE))
	g.db.commit()

	Critter.from_name(filename, owner_id=owner.id).compile()

def process_file(content, owner, filename):
	"""Process a raw code file to be compiled."""
	prepends = []
	prepends.append("package battlecritters.critters.{owner};".format(owner=owner))
	prepends.append("import battlecritters.battle.Critter;".format(owner=owner))
	prepends.append("import battlecritters.battle.CritterInfo;".format(owner=owner))
	content = "\n".join(prepends) + "\n" + content
	return content

def check_filename(filename):
	"""Returns True if filename is a valid name for a Critter, else returns False."""
	if len(filename) < 1 or len(filename) > MAX_CLASS_NAME_LENGTH:
		return False
	if filename in JAVA_KEYWORDS:
		return False
	if filename[0] not in JAVA_LETTERS:
		return False
	for c in filename:
		if c not in JAVA_LETTERS_OR_DIGITS:
			return False
	return True

def format_compiler_output(s):
	"""Formats the output of the java compiler to be displayed in the editor."""
	# Remove filepaths
	search = r'\./java/temp_critters/(\w*.java)'
	replace = r'\1'
	s = re.sub(search, replace, s)
	# Fix line numbers
	search = r'(\w*.java:)(\d+)'
	replace = lambda m: m.groups()[0] + str(int(m.groups()[1]) - 3)
	s = re.sub(search, replace, s)

	# HTML line breaks
	s = s.replace("\n", "<br>")
	# Non breaking spaces
	s = s.replace(' ', '&nbsp;')
	return s