"""
Handles the model, as well as pages for editing and viewing, of critter code.
"""

from flask import abort, Blueprint, Flask, g, jsonify, Markup, redirect, render_template, request, session, url_for
import os
import re
import sqlite3
import string
import subprocess
import sys
import time
import traceback
import zlib

from util import json_service, login_required, admin_required, require_user
import battles
import ranking
import users
import util

JAVA_KEYWORDS = {'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float', 'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void', 'volatile', 'while'} 
JAVA_LETTERS = {c for c in string.ascii_letters}
JAVA_DIGITS = {c for c in string.digits}
JAVA_LETTERS_OR_DIGITS = JAVA_LETTERS | JAVA_DIGITS
MAX_CLASS_NAME_LENGTH = 128
COMPRESSION_LEVEL = 1
DEFAULT_CONTENT = ""
with open(os.path.join('static', 'default_critter.java')) as f:
	DEFAULT_CONTENT = f.read()

editor_app = Blueprint('editor_app', __name__, template_folder='templates')


def init():
	"""Initialize the module"""
	global Battle, User
	Battle = battles.Battle
	User = users.User

class Critter(object):
	"""A model for a Critter. Handles database comunication. To load a Critter, use one of the static methods."""

	@staticmethod
	def from_name(filename, owner=None, owner_id=None, owner_name=None, fail_silent=False, columns=[]):
		"""Load a Critter from an owner and filename"""
		if owner_id == None:
			if owner == None:
				owner = users.User.from_username(owner_name)
			owner_id = owner.id

		columns = ', '.join({column for column in columns + ['id', 'name', 'owner_id']})
		row = g.db.execute("SELECT " + columns + " FROM critters WHERE owner_id=? AND name=?", (owner_id, filename)).fetchone()
		if row is None:
			if fail_silent:
				return None
			else:
				e = LookupError("Critter not found: " + filename)
				e.status_code = 404
				raise e
		return Critter(row)

	@staticmethod
	def from_id(id, fail_silent=False, columns=[]):
		"""Load a critter from id"""
		columns = ', '.join({column for column in columns + ['id', 'name', 'owner_id']})
		row = g.db.execute("SELECT " + columns + " FROM critters WHERE id=?", (id,)).fetchone()
		if row is None:
			if fail_silent:
				return None
			else:
				raise LookupError("Critter not found: " + str(id))
		return Critter(row)
	
	def __init__(self, row):
		"""Create a new critter from a database row"""
		self.id = row['id']
		self.name = row['name']
		self.owner_id = row['owner_id']
		self._content = zlib.decompress(row['content']) if ('content' in row) else None
		self._compiled_content = zlib.decompress(row['compiled_content']) if ('compiled_content' in row) else None
		self._public = row['public'] if ('public' in row) else None
		self._creation_time = row['creation_time'] if ('creation_time' in row) else None
		self._last_save_time = row['last_save_time'] if ('last_save_time' in row) else None
		self._last_compile_time = row['last_compile_time'] if ('last_compile_time' in row) else None
		self._score = row['score'] if ('score' in row) else None
		self._owner = None

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
			self._content = zlib.decompress(g.db.execute("SELECT content FROM critters WHERE id = ?", (self.id,)).fetchone()['content'])
		return self._content

	@content.setter
	def content(self, value):
		self._content = value
		current_time = time.time()
		zcontent = zlib.compress(self._content, COMPRESSION_LEVEL)
		g.db.execute("UPDATE critters SET content = ?, last_save_time = ? WHERE id = ?;", (zcontent, current_time, self.id))
		self.last_save_time = current_time

	@property
	def compiled_content(self):
		"""Last compiled content of this Critter"""
		if self._compiled_content == None:
			self._compiled_content = zlib.decompress(g.db.execute("SELECT compiled_content FROM critters WHERE id = ?", (self.id,)).fetchone()['compiled_content'])
		return self._compiled_content

	@compiled_content.setter
	def compiled_content(self, value):
		self._compiled_content = value
		zcontent = zlib.compress(value, COMPRESSION_LEVEL)
		g.db.execute("UPDATE critters SET compiled_content = ? WHERE id = ?;", (zcontent, self.id))
	
	@property
	def score(self):
		"""The score of this Critter"""
		if self._score == None:
			self._score = g.db.execute("SELECT score FROM critters WHERE id=?", (self.id,)).fetchone()['score']
		return self._score

	@score.setter
	def score(self, value):
		self._score = value
		g.db.execute("UPDATE critters SET score = ? WHERE id = ?;", (self._score, self.id))
	
	@property
	def public(self):
		"""Whether or not this critter is visible to the public."""
		if self._public == None:
			self._public = g.db.execute("SELECT public FROM critters WHERE id=?", (self.id,)).fetchone()['public']
		return self._public

	@public.setter
	def public(self, value):
		self._public = value
		g.db.execute("UPDATE critters SET public=? WHERE id = ?;", (self._public, self.id))

	@property
	def creation_time(self):
		"""The last time this critter was created."""
		if self._creation_time == None:
			self._creation_time = g.db.execute("SELECT creation_time FROM critters WHERE id=?", (self.id,)).fetchone()['creation_time']
		return self._creation_time

	@creation_time.setter
	def creation_time(self, value):
		self._creation_time = value
		g.db.execute("UPDATE critters SET creation_time=? WHERE id = ?;", (self._creation_time, self.id))

	@property
	def last_save_time(self):
		"""The last time this critter was saved."""
		if self._last_save_time == None:
			self._last_save_time = g.db.execute("SELECT last_save_time FROM critters WHERE id=?", (self.id,)).fetchone()['last_save_time']
		return self._last_save_time

	@last_save_time.setter
	def last_save_time(self, value):
		self._last_save_time = value
		g.db.execute("UPDATE critters SET last_save_time=? WHERE id = ?;", (self._last_save_time, self.id))

	@property
	def last_compile_time(self):
		"""The last time this critter was compiled"""
		if self._last_compile_time == None:
			self._last_compile_time = g.db.execute("SELECT last_compile_time FROM critters WHERE id=?", (self.id,)).fetchone()['last_compile_time']
		return self._last_compile_time

	@last_compile_time.setter
	def last_compile_time(self, value):
		self._last_compile_time = value
		g.db.execute("UPDATE critters SET last_compile_time=? WHERE id = ?;", (self._last_compile_time, self.id))

	def get_all_battles(self):
		"""Return the list of battles this critter been in"""
		return map(battles.Battle.from_id, [row.id for row in g.db.execute("SELECT battle_id FROM battle_critters WHERE critter_id = ?", (self.id,)).fetchall()])

	def get_recent_battles(self, limit=20):
		"""Return the list of the limit most recent battles this critter has been in."""
		limit = int(limit)
		rows = g.db.execute("SELECT DISTINCT battles.id FROM battles, battle_critters, critters \
			WHERE battles.id=battle_critters.battle_id \
			AND battle_critters.critter_id=? \
			ORDER BY battles.creation_time DESC \
			LIMIT ?;", (self.id, limit)).fetchall()
		return [battles.Battle.from_id(row[0]) for row in rows]

	def get_winning_battles(self):
		"""Return the list of battles this critter has won"""
		return map(battles.Battle.from_id, [row.id for row in g.db.execute("SELECT battle_id FROM battle_critters WHERE critter_id = ? AND place = 1", (self.id,)).fetchall()])
	
	def get_losing_battles(self):
		"""Return the list of battles this critter has not won"""
		return map(battles.Battle.from_id, [row.id for row in g.db.execute("SELECT battle_id FROM battle_critters WHERE critter_id = ? AND place > 1", (self.id,)).fetchall()])

	def get_ranked_wins(self):
		"""Return the number of wins in ranked battles"""
		query = "SELECT COUNT(*) FROM battle_critters, battles \
		WHERE battles.id = battle_critters.battle_id \
		AND critter_id = ? AND place = 1 AND ranked = 1"
		row = g.db.execute(query, (self.id,)).fetchone()
		return row[0]

	def get_ranked_losses(self):
		"""Return the number of wins in ranked battles"""
		query = "SELECT COUNT(*) FROM battle_critters, battles \
		WHERE battles.id = battle_critters.battle_id \
		AND critter_id = ? AND place > 1 AND ranked = 1"
		row = g.db.execute(query, (self.id,)).fetchone()
		return row[0]

	def get_url(self, action="view"):
		"""Return a url for any type of view."""
		if action == 'view':
			return url_for('editor_app.view_file', owner=self.owner.username, filename=self.name)
		elif action == 'edit':
			return url_for('editor_app.view_file', owner=self.owner.username, filename=self.name)
		elif action == 'save':
			return url_for('editor_app.save_file', owner=self.owner.username, filename=self.name)
		elif action == 'compile':
			return url_for('editor_app.compile_file', owner=self.owner.username, filename=self.name)
		elif action == 'revert':
			return url_for('editor_app.revert_file', owner=self.owner.username, filename=self.name)
		else:
			raise Exception("Unknown Action: " + action)

	def get_link(self, action='view', text="{owner}.{name}"):
		"""Return an HTML snippet with a link to the userpage. If text is none, defaults to 'ownername.name' ."""
		url = self.get_url(action)
		text = text.format(name = self.name, owner=self.owner.username, id=self.id, url=url)
		return Markup("<a href='{url}' class='crittername'>{text}</a>".format(url=url,text=text))

	def revert(self):
		"""Reverts content back to last compiled content."""
		self.content = self.compiled_content

	def compile(self):
		"""Compile the critter."""
		# TODO: Switch os compiling to java compiling. I think it should be faster.
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
			# on success, update compiled content
			current_time = time.time()
			self.compiled_content = self.content
			g.db.execute("UPDATE critters SET last_compile_time = ? WHERE id = ?;", (current_time, self.id))
			return {'success': True}
		except subprocess.CalledProcessError as e:
			errors = parse_compiler_output(e.output)
			return {'success': False, 'errors': errors}

	def reload(self):
		"""Reload all the data from this critter out of the database.""" 
		row = g.db.execute("SELECT * FROM critters WHERE owner=? AND name=?", (owner_id, filename)).fetchone()
		if row is None:
			raise LookupError("Critter not found: " + filename)
		self.__init__(row)

	def delete(self):
		"""Delete the critter"""
		# delete from database
		g.db.execute("DELETE FROM critters WHERE id = ?;", (self.id,))

		# remove compiled file
		path = os.path.join('.', 'java', 'bin', 'critters', owner, filename + '.class')
		os.remove(path)

	def as_object(self, name=True, owner=True, score=True, url=True, wins=True, losses=True, content=False):
		"""Return an object ready to be converted to json. Specify the parameters to be included."""
		data = {}
		data['id'] = self.id
		if name:
			data['name'] = self.name
		if owner:
			data['owner_name'] = self.owner.username
			data['owner_id'] = self.owner.id
		if score:
			data['score'] = self.score
		if url:
			data['url'] = self.get_url()
		if content:
			data['content'] = self.content
		if wins:
			data['wins'] = self.get_ranked_wins()
		if losses:
			data['losses'] = self.get_ranked_losses()
		return data

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
@json_service
def get_critters_json():
	"""Returns a map of critter id to information such as name, owner_name, and owner_id for ids from the request."""
	r = {}
	for critter_id in request.args.getlist('ids[]'):
		c = Critter.from_id(critter_id)
		r[c.id] = c.as_object()
	return r

@editor_app.route('/json/user')
@json_service
def get_critters_json_user():
	"""Returns a map of critter id to information such as name, owner_name, and owner_id."""
	r = {'critters': []}
	for c in g.user.get_critters():
		r['critters'].append(c.as_object())
	return r

@editor_app.route('/get_ids/user')
@json_service
def get_user_critter_ids():
	"""Return a list of critter ids"""
	limit = request.args['limit']
	owner_id = g.user.id
	query = "SELECT id FROM critters WHERE owner_id=? ORDER BY id LIMIT ?"
	rows = g.db.execute(query, (owner_id,limit)).fetchall()
	ids = [row['id'] for row in rows]
	return {'ids': ids}

@editor_app.route('/get_ids/random')
@json_service
def get_random_critter_ids():
	"""Return a list of critter ids"""
	if 'limit' in request.args:
		limit = request.args['limit']
	else:
		limit = 128
	owner_id = g.user.id
	rows = g.db.execute("SELECT id FROM critters ORDER BY RANDOM() LIMIT ?", (limit,)).fetchall()
	ids = [row['id'] for row in rows]
	return {'ids': ids}

@editor_app.route('/get_battles/recent')
@json_service
def get_critter_recent_battles():
	"""Return a list of resent battles for the critter"""
	r = {'battles': []}
	if 'critter_id' in request.args:
		critter = Critter.from_id(request.args['critter_id'])
	else:
		raise Exception("critter_id not specified")
	for battle in critter.get_recent_battles():
		data = {}
		data['height'] = battle.height
		data['id'] = battle.id
		data['length'] = battle.length
		data['pretty_time'] = util.format_date(battle.creation_time)
		data['ranked'] = battle.ranked
		data['time'] = battle.creation_time
		data['url'] = battle.get_url()
		data['width'] = battle.width
		data['place'] = battle.get_critter_place(critter)
		r['battles'].append(data)
	return r

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

@editor_app.route('/<owner>/<filename>')
def view_file(owner, filename):
	try:
		critter = Critter.from_name(filename, owner_name=owner)
		return render_template('edit_critter.html', critter=critter)
	except LookupError as e:
		abort(404)

@editor_app.route('/<owner>/<filename>', methods=['PUT', 'POST'])
@json_service
def save_file(owner, filename):
	require_user(owner)
	critter = Critter.from_name(filename, owner_name=owner)
	critter.content = request.form['content']

@editor_app.route('/<owner>/<filename>', methods=['DELETE'])
@json_service
def delete_file(owner, filename):
	"""Delete a file if it exists"""
	owner_id = users.User.from_username(owner).id
	# throws error if it doesn't exists
	Critter.from_name(filename, owner_id=owner_id, fail_silent=False).delete()

@editor_app.route('/<owner>/<filename>/compile', methods=["GET","POST"])
@json_service
def compile_file(owner, filename):
	"""Compile a file. User must be the owner of the critter or an admin."""
	require_user(owner)
	critter = Critter.from_name(filename, owner_name=owner)
	return critter.compile()

@editor_app.route('/<owner>/<filename>/revert', methods=["GET","POST"])
@json_service
def revert_file(owner, filename):
	"""Revert a file to its last compiled text. User must be the owner of the critter or an admin. Returns the neew (old) content of the critter."""
	require_user(owner)
	critter = Critter.from_name(filename, owner_name=owner)
	critter.revert()
	return {'content': critter.content}

@editor_app.route('/<owner>/create_new', methods=["POST", "PUT"])
@json_service
def new_file(owner):
	"""Create a new file. name should be specified in the request"""
	require_user(owner)
	if 'name' not in request.form:
		raise Exception("No name specified")
	filename = request.form['name']
	if not check_filename(filename):
		raise Exception("Invalid Class Name")
	owner = users.User.from_username(owner)
	create_file(owner, filename, request.form.get("content"))

def create_file(owner, filename, content=None):
	"""Actually create a new critter"""
	if (Critter.from_name(filename, owner=owner, fail_silent=True) != None):
		raise Exception("File already exists")

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

def parse_compiler_output(s):
	"""Return a dictionary mapping line number to error message"""
	errors = {}
	pattern = re.compile(r'\./java/temp_critters/(\w*.java):(\d+):')
	for line in s.split("\n"):
		# find lines that describe errors
		match = pattern.match(line)
		if match is not None:
			line = pattern.sub("", line)
			line = re.sub(r'',"", line)
			number = int(match.expand(r'\2')) - 3 # subtract 3 for invisible lines at top of file
			errors[number] = line
	errors['full'] = s
	return errors



	# # Remove filepaths
	# replace = r'\1'
	# s = re.sub(search, replace, s)
	# # Fix line numbers
	# search = r'(\w*.java:)(\d+)'
	# replace = lambda m: m.groups()[0] + str(int(m.groups()[1]) - 3)
	# s = re.sub(search, replace, s)

	# # HTML line breaks
	# s = s.replace("\n", "<br>")
	# # Non breaking spaces
	# s = s.replace(' ', '&nbsp;')
	# return s