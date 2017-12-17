#################################################
#												#
# This class takes in a text file input of the	#
# tax defaulters list, and parses it to extract #
# individual defaulter information such as 		#
# name, address and fine amount.				#
#												#
# Author:  Shane Brennan						#
# Date:    20171216								#
# Version: 0.1									#
#################################################

import io
import re
import os
import csv
import sys
import json
import time
import logging
import datetime
import collections
from sets import Set
from Defaulter import Defaulter
from optparse import OptionParser
from logging.handlers import RotatingFileHandler

class ProcessDefaulters:

	def __init__(self, configDict=None):

		self.keywordList    = {}
		self.keywordSet     = Set()
		self.logger         = None

		self.defaultersList = []

		if configDict is not None:
			self.setupLogging(configDict, False)
			self.run(configDict, False)

	def setupLogging(self, configDict, flaskApp=False):
                """ Sets up the rotating file logger for the parser. This records logs to a
                    specified backup location, in this case ./logs/parser.log. The log file location
                    is stored in a JSON configuration script passed to the CreateFeatures at runtime.

		    configDict - A dict object containing configuration settings
		    flaskApp   - A register to flag whether the class is being run as a Flask Application
                """
		if not flaskApp:
			self.logger = logging.getLogger(__name__)
			handler = RotatingFileHandler(configDict['log-filename'], maxBytes=500000, backupCount=3)
			format  = "%(asctime)s %(levelname)-8s %(message)s"
			handler.setFormatter(logging.Formatter(format))
			handler.setLevel(logging.INFO)
			self.logger.addHandler(handler)
			self.logger.setLevel(logging.INFO)
			self.logger.info('Starting ProcessDefaulters script..')
		else:
			self.logger = logging.getLogger('App')

	def run(self, configDict, flaskApp=False):
		""" 
		   Called to run the processing of the defaulters, instantiate the 
		   defaulters list and execute the summary analysis.

		   configDict - A dict object containing configuration settings		
		   flaskApp   - A register to flag whether the class is being run as a Flask Application
		"""

		# Retrieve the data folder
		dir = configDict['data-folder']

		# Parse the folder for the files
		for root, dirs, files in os.walk(dir):
			path = root.split(os.sep)
			for filename in files:
				if filename[-4:] == '.txt':
					if self.logger is not None:
						self.logger.info('Reading input data file {0}'.format(filename))
					self.processFile(root+os.sep+filename)

		# Log the output
		if self.logger is not None:
			self.logger.info('Processed {0} defaulters'.format(len(self.defaultersList)))


	def processFile(self, inputFilename):
		""" 
		   The processFile() function iterates over each section. Basically 
		   this operates in three passes, first to assign the types to each 
		   line in the input file, second to adjust the lines which contain
		   the charges, and lastly to process each defaulter line. 
	
		   inputFilename - The name and path of the file to be processed
		"""

		reader           = self.unicodeReader(open(inputFilename, 'rU'))
		emptyRegex       = re.compile('^\s*$')
		pageRegex        = re.compile('^\s+[0-9]+$')
		headerRegex      = re.compile('^(Name){1}\s+(Address)')
		notesRegex       = re.compile('^\s*[a-zA-Z]{1}[a-z]+')

		lines        = []
		lineTypes    = []
		index        = 0

		# The first pass to figure out whos a 
		# defaulter and who's not.
		for line in reader:
			lines.append(line)
			if emptyRegex.match(line):
				lineTypes.append('EMPTY')
			elif pageRegex.match(line):
				lineTypes.append('PAGE')
			elif headerRegex.match(line):
				lineTypes.append('HEADER')
			elif notesRegex.match(line):
				lineTypes.append('NOTES')
			else:
				lineTypes.append('DEFAULTER')
			index += 1

		# Find and set the lines with the charges
		lastDefaulterIndex = 0
		for index, type in enumerate(lineTypes):
			if type == 'DEFAULTER':
				lastDefaulterIndex = index
			elif type == 'HEADER':
				lineTypes[lastDefaulterIndex] = 'CHARGE'

		currentCharge = 'UNKNOWN'

		for index, type in enumerate(lineTypes):
			line = lines[index]
			if type == 'CHARGE':
				currentCharge = line
			elif type == 'DEFAULTER' and lineTypes[index-1] != 'DEFAULTER':
				defaulter = Defaulter(line.rstrip())
				defaulter.addCharge(currentCharge)
				self.defaultersList.append(defaulter)
			elif type == 'DEFAULTER' and lineTypes[index-1] == 'DEFAULTER':			
				self.defaultersList[-1].update(line.rstrip())

		if self.logger is not None:
			self.logger.info('Added {0} defaulters'.format(len(self.defaultersList)))


        def unicodeReader(self, fileReader):
		""" 
		    A more robust file reader that can handle nonsense characters, 
		    null bytes and the like.
		"""
		while True:
			try:
				yield next(fileReader)
			except csv.Error:
				pass
			continue
		return


	def getNumDefaulters(self):
		return len(self.defaultersList)


	def getDefaulter(self, name):
		tokens = name.upper().replace(',',' ').split(' ')
		for defaulter in self.defaultersList:
			result = True
			for token in tokens:
				if token not in defaulter.getName():
					result = False
			if result:
				return defaulter
		return None

def getConfig(filename):
	""" 
	This function reads in the JSON configuration file, found in the /conf folder 
	in the repository, which contains all the setup details for the system. 
	"""
	try:
		with open(filename) as jsonFile:
			config = json.load(jsonFile)
			return config
	except Exception, err:
		print 'Error reading in configuration file {0}'.format(filename)
		print 'Description - {0}'.format(str(err))
		print 'Exiting ...'
		exit(1)

def main(argv):
	parser = OptionParser(usage="Usage: ProcessDefaulters <config-json>")
	(options, filename) = parser.parse_args()

	if len(filename) == 1:
		if os.path.exists(filename[0]):
			configDict = getConfig(filename[0])
			processor  = ProcessDefaulters(configDict)
		else:
			parser.print_help()
			print '\nYou need to provide a config file as input.'
			exit(1)
	else:
                parser.print_help()
                print '\nYou need to provide a config file as input.'
                exit(1)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
