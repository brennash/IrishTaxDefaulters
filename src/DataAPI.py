import io
import os
import csv
import re
import json
import smtplib
import logging
import datetime
from flask import render_template
from flask import session
from flask import make_response, send_from_directory, redirect, url_for
from flask import Flask, request, Response
from functools import wraps
from logging.handlers import RotatingFileHandler

# Setup the app, with a random secret key for the sessions
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.secret_key = os.urandom(24).encode('hex')

# Document list


# The main index page
@app.route('/api')
def index():
	return render_template('index.html')


if __name__ == '__main__':
	handler = RotatingFileHandler('log/api.log', maxBytes=50000, backupCount=3)
	format = "%(asctime)s %(levelname)-8s %(message)s"
	handler.setFormatter(logging.Formatter(format))
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	app.run(host='0.0.0.0', port=1798, debug=True)
