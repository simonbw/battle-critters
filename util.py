"""
Assorted Utility functions and classes for doing all sorts of things. Does not depend on any of my files.
"""

import datetime
import time

def format_date(seconds):
	"""Return a date formatted nicely"""
	now = datetime.datetime.today()
	date = datetime.datetime.fromtimestamp(seconds)
	if date.date() == now.date():
		return date.strftime('%I:%M %p')
	return date.strftime('%a %H:%M %p')