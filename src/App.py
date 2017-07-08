from flask import render_template
from flask import session
from flask import make_response, send_from_directory, redirect, url_for
from flask import Flask, request, Response
from functools import wraps
import io
import os
import csv
import datetime
import re
import json
import smtplib
import logging
import pickle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging.handlers import RotatingFileHandler

# Setup the app, with a random secret key for the sessions
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.secret_key = os.urandom(24).encode('hex')

# The main index page
@app.route('/')
def index():
	return render_template('index.html')

# Page to select the weekly sales
@app.route('/weekly_sales/', methods=['GET','POST'])
def weeklySales():
	if request.method == 'GET':
		reqIPAddr = request.remote_addr
		app.logger.info('Weekly sales request (HTTP GET) from - {0}'.format(reqIPAddr))
		return render_template('weekly_sales.html')
	else:
		reqIPAddr = request.remote_addr
		app.logger.info('Weekly sales request (HTTP POST) from - {0}'.format(reqIPAddr))
		return render_template('weekly_sales.html')


if __name__ == '__main__':
	handler = RotatingFileHandler('log/dashboard.log', 
			maxBytes=50000, 
			backupCount=3)
	format = "%(asctime)s %(levelname)-8s %(message)s"
	handler.setFormatter(logging.Formatter(format))
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	app.run(host='0.0.0.0', port=1798, debug=True)
