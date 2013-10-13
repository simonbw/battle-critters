"""
Module for managing all the basic info pages.
"""

from flask import Blueprint, g, render_template, request, redirect, session, url_for, flash

info_app = Blueprint('info_app', __name__, template_folder='templates')

