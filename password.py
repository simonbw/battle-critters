"""
Handles hashing of passwords.
"""

import hashlib

def hash_password(password, username):
	"""Hash a user's password"""
	h = hashlib.sha512()
	h.update(password)
	h.update(username)
	return h.hexdigest()