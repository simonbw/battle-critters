"""
Used to compute elo rankings.
"""

DEFAULT_SCORE = 100

from flask import abort, Blueprint, Flask, g, jsonify, Markup, redirect, render_template, request, session, url_for
import os
import re
import sqlite3
import string
import traceback

from util import json_service, login_required, admin_required, require_user
import battles
import editor
import ranking
import users
import util

ranking_app = Blueprint('ranking_app', __name__, template_folder='templates')

def init():
	"""Initialize the module"""
	global Battle, User, Critter
	Battle = battles.Battle
	User = users.User
	Critter = editor.Critter
	print "ranking_app initialized"


@ranking_app.route('/leaderboard')
@util.error_checked
def leaderboard_page():
	rows = g.db.execute("SELECT id, name, owner_id, score FROM critters ORDER BY score DESC LIMIT 100")
	critters = enumerate([Critter(row) for row in rows], 1)
	return render_template('leaderboard.html', critters=critters)