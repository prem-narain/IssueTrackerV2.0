'''
   Serves Flask static pages
'''
from flask import (Flask, Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, abort, jsonify, send_from_directory)
from flask.ext.login import login_required, login_user, current_user, logout_user, confirm_login, login_fresh

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def index(path=None):   
   return render_template('app.html')

@frontend.route('/dashboard', methods=['GET'])
@login_required	
def home(path=None):
	return render_template('home.html')	

@frontend.route('/create_issue', methods=['GET'])
@login_required
def issue():
	return render_template('create_issue.html')