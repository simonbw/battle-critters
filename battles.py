"""
Create and view battles.
"""

import random
import sys
import time
import traceback

import sqlite3
from flask import Flask, g, redirect, request, session, render_template, Blueprint, url_for, Markup, abort

import users
import util
from editor import Critter

battles_app = Blueprint('battles_app', __name__, template_folder='templates')

class Battle():
	"""A model. Interacts with the database. Use from_id to load a battle from the database."""
	@staticmethod
	def from_id(id):
		"""Load a battle from the database based on its id."""
		row = g.db.execute("SELECT * FROM battles WHERE id=?", (id,)).fetchone()
		if row is None:
			raise LookupError("Battle not found: " + str(id))
		return Battle(row)

	def __init__(self, row):
		"""Create a battle from a database row."""
		self.id = row['id']
		self.creation_time = row['creation_time']
		self.length = row['length']
		self.width = row['width']
		self.height = row['height']

		if self.id is None or self.creation_time is None:
			raise ValueError("Improper row given to Battle")

	def get_winner(self):
		"""Return the Critter that won the battle."""
		rows = g.db.execute("SELECT critter_id, winner FROM battle_critters WHERE battle_id=?", (self.id,)).fetchall()
		for row in rows:
			if row['winner'] == 1:
				return Critter.from_id(row['critter_id'])

	def get_critters(self):
		"""Return a list of critters competing in this battle."""
		rows = g.db.execute("SELECT critter_id, position FROM battle_critters WHERE battle_id=?", (self.id,)).fetchall()
		return [Critter.from_id(row['critter_id']) for row in rows]

	def get_frames(self, start, end):
		"""Return the data for the frames of the battle."""
		query = "SELECT * FROM battle_frames WHERE battle_id=? AND frame_number>=? AND frame_number<=?;"
		rows = g.db.execute(query, (self.id, start, end)).fetchall()
		lines = ["FRAME " + str(row['frame_number']) + "\n" + row['data'] for row in rows]
		return "\n".join(lines)

	def get_frame_url(self):
		"""Return the url for getting this battle's frames"""
		return Markup(url_for('battles_app.get_frames', battle_id=self.id))

	def get_url(self):
		"""Return the url for viewing this battle."""
		return Markup(url_for('battles_app.view_battle', battle_id=self.id))

	def get_pretty_time(self):
		"""Return a nicely formatted version of the time"""
		return util.format_date(self.creation_time)

	def get_link(self, text=None):
		"""Return an HTML snippet with a link to the userpage. If text is none, defaults to the username."""
		if text is None:
			text = self.get_pretty_time()
		return Markup("<a href='{url}' class='battle'>{text}</a>".format(url=self.get_url(),text=text))


@battles_app.route('/')
def recent_battles_page():
	"""View recent battles."""
	battles = map(Battle, g.db.execute('SELECT * FROM battles ORDER BY creation_time DESC LIMIT 10').fetchall())
	return render_template('recent_battles.html', battles=battles)

@battles_app.route('/<int:battle_id>')
def view_battle(battle_id):
	"""View a battle."""
	battle = Battle.from_id(battle_id)
	return render_template('view_battle.html', battle=battle, critters=battle.get_critters())

@battles_app.route('/<int:battle_id>/frames')
def get_frames(battle_id):
	"""Return data for certain frames of a battle.
	request.args['start'] and request.args['end'] should be set."""
	battle = Battle.from_id(battle_id)
	start = int(request.args['start'])
	end = int(request.args['end'])
	return battle.get_frames(start, end)
	
@battles_app.route('/new', methods=["GET"])
def new_battle_page():
	"""The page for creating a new battle."""
	if request.method == "GET":
		return render_template('new_battle.html')
	elif request.method == "POST":
		try:
			length = request.form['length']
			width = request.form['width']
			height = request.form['height']
			ranked = bool(request.form['ranked'])

			critters = []
			for owner_name, critter_name in zip(request.form.getlist('owners[]'), request.form.getlist('critters[]')):
				critters.append(editor.Critter.from_name(critter_name, owner_name=owner_name))

			create_battle(length, width, height, critters, ranked)
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
			return Markup("ERROR: " + repr(e))

def create_battle(length, height, width, critters, ranked):
	"""Actually create a new battle"""

	#create database entry
	current_time = time.time()
	cursor = g.db.execute('INSERT INTO battles (creation_time, length, width, height, ranked) VALUES (?,?,?,?,?);', (current_time, length, width, height, int(ranked)))
	battle_id = cursor.lastrowid
	
	jbattle = g.java_server.createBattle(length, width, height)

	# add critters
	position = 0
	for critter in critters:
		g.db.execute("INSERT INTO battle_critters (battle_id, critter_id, position) VALUES (?,?,?)", (battle_id, critter.id, position))
		position += 1
		print "python adding critter:", owner_name + '.' + critter_name + "({0}{1})".format(critter.id, critter.name)
		jbattle.addCritter(owner_name, critter_name)

	jbattle.start()

	# run battle
	while not jbattle.isOver():
		data = jbattle.toString()
		frame = jbattle.getFrame()
		g.db.execute("INSERT INTO battle_frames (battle_id, frame_number, data) VALUES (?, ?, ?)", (battle_id, frame, data))
		jbattle.nextFrame()

	# update scores
	owner_name, critter_name = jbattle.getWinner().split('.')
	winner = Critter.from_name(critter_name, owner_name=owner_name)
	g.db.execute("UPDATE battle_critters SET winner = 1 WHERE critter_id = ?", (winner.id,))
	g.execute.db("UPDATE critters SET score = score + ? WHERE id = ?", (score_change, winner.id))

	# for loser in jbattle.getLosers():
	# 	owner_name, critter_name = loser.split('.')
	# 	loser = Critter.from_name(critter_name, owner_name=owner_name)
	# 	g.db.execute("UPDATE critters SET score = score - ? WHERE id = ?", (score_change, loser.id))
	
	g.db.commit()

	return str(battle_id)