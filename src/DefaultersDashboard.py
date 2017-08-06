#########################################################################################################################
# 															#
# The Defaulters Dashboard provides a searchable front end and D3.js dashboard for the Irish Tax Defaulters listings.   #
# Note, that no data is actually stored by this repository, only processed from a publicly-available data source        #
# provided by the revenue. Since the revenue only make a certain number of historical files available, not all historic #
# data can be accessed. 												#
#															#
# Date:    6th August 2017												#
# Version: 1.0														#
#########################################################################################################################

import re
import io
import os
import csv
import datetime
import hashlib
import logging
from flask import session
from functools import wraps
from Defaulter import Defaulter
from flask import render_template
from flask import Flask, request, Response
from ProcessDefaulters import ProcessDefaulters
from logging.handlers import RotatingFileHandler
from flask import make_response, send_from_directory, redirect, url_for

# Call the flask application
app = Flask(__name__)

# Setup the app, with a random secret key for the sessions
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.secret_key = os.urandom(24).encode('hex')

# Initialize the defaulters dataset
defaulters = ProcessDefaulters()
defaulters.loadFiles('data')

# The main index page
@app.route('/')
def index():
	# Get the request IP Address
	reqIPAddr = request.remote_addr

	# Log the requestor details to file
	app.logger.info('User Request to index.html: {0}'.format(reqIPAddr))
	app.logger.info('Request URL: {0}'.format(request.url))
	app.logger.info('User Platform: {0}'.format(request.user_agent.platform))
	app.logger.info('User Browser: {0}'.format(request.user_agent.browser))
	app.logger.info('User Agent Version: {0}'.format(request.user_agent.version))
	app.logger.info('User Agent Language: {0}'.format(request.user_agent.language))
	app.logger.info('User Agent String: {0}'.format(request.user_agent.string))
	return render_template('index.html')

@app.route('/search', methods=['GET','POST'])
def search():
	# Get the request IP Address
	reqIPAddr = request.remote_addr
	app.logger.info('Search Request: {0}'.format(reqIPAddr))

	if request.method == 'POST':
		# Log the requestor details to file
		searchStr = request.form.get('search_text')
		app.logger.info('Search String: {0}'.format(searchStr))
		resultList = defaulters.searchKeywords(searchStr.strip().lower())
		app.logger.info('Returned {0} defaulters'.format(len(resultList)))
		return render_template('search.html', defaulterList=resultList)
	else:
		app.logger.warning('GET request to /search endpoint: {0}'.format(reqIPAddr))
		return redirect(url_for('index'))



@app.route('/autocomplete', methods=['GET'])
def autocomplete():
	search = request.args.get('q')
	query = db_session.query(Movie.title).filter(Movie.title.like('%' + str(search) + '%'))
	results = [mv[0] for mv in query.all()]
    	return jsonify(matching_results=results)

#@app.route('/submit/', methods=['GET','POST'])
#def submit():
#	if request.method == 'POST':
#		reqIPAddr = request.remote_addr
#		app.logger.info('submit.html request from - {0}'.format(reqIPAddr))
#


# The main calling class, running off port 1592
if __name__ == '__main__':
	handler = RotatingFileHandler('log/dashboard.log', maxBytes=50000, backupCount=3)
	format = "%(asctime)s %(levelname)-8s %(message)s"
	handler.setFormatter(logging.Formatter(format))
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	app.logger.setLevel(logging.INFO)
	app.run(host='0.0.0.0', port=1798)
