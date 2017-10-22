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
		self.charges        = Set()
		self.logger         = None
		self.defaultersList = []

		if configDict is not None:
			self.setupLogging(configDict,False)
			self.run(configDict)

	def setupLogging(self, configDict, flaskApp=False):
                """ Sets up the rotating file logger for the parser. This records logs to a
                    specified backup location, in this case ./logs/parser.log. The log file location
                    is stored in a JSON configuration script passed to the CreateFeatures at runtime.
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

	def run(self, configDict):
		""" 
		Called to run the processing of the defaulters, instantiate the 
		defaulters list and execute the summary analysis.
		"""
		self.loadFiles(configDict['data-folder'])
		self.printSummary()

	def loadFiles(self, dir):
		""" 
		Recursively parses through a provided input data folder, extracting 
		and reading all the input files therein.

		@dir - The string describing the root data directory.
		"""

		# Parse the folder for the files
		for root, dirs, files in os.walk(dir):
			path = root.split(os.sep)
			for filename in files:
				if filename[-4:] == '.txt':
					if self.logger is not None:
						self.logger.info('Reading input data file {0}'.format(filename))
					self.processFile(root+os.sep+filename)
		# Try to log the output
		if self.logger is not None:
			self.logger.info('Processed {0} defaulters'.format(len(self.defaultersList)))

		# Process the keywords for indexing and lookup
		self.processKeywords()


	def processFile(self, inputFilename):
		""" 
		The processFile() function iterates over each section.
		"""

		inputText, charges, sectionStart, sectionEnd = self.getSections(inputFilename)

		# Add any new charges
		for charge in charges:
			self.charges.add(charge)

		for index, startIndex in enumerate(sectionStart):
			endIndex             = sectionEnd[index]
			charge               = charges[index]
			self.defaultersList += self.processSection(inputText, charge, startIndex, endIndex)

		if self.logger is not None:
			self.logger.info('Processed {0} defaulters in {1}'.format(len(self.defaultersList), inputFilename))


	def processSection(self, inputText, charge, startIndex, endIndex):
		""" 
		Process the list of defaulters, section by section.  
		"""

		defaulterList = []
		pageRegex     = re.compile('^\s{20,}[0-9]+$')
		for index, line in enumerate(inputText):
			if startIndex <= index and index <= endIndex and 'Defaulters' not in line and not pageRegex.match(line):
				startLine, endLine, totalChars = self.parseLine(line)
				if totalChars > 50 and startLine == 0:
					defaulterList.append(Defaulter(line=line, lineNumber=index, verboseFlag=False))
					defaulterList[-1].addCharge(charge)
				elif len(defaulterList) > 0:
					defaulterList[-1].update(line)
		return defaulterList


	def getSections(self, inputFilename):
		""" 
		Reads the input file and splits out the text by sections, 
		record the start/end index, and type of charge for each section
		as lists.

		@inputText    - The input text of the file as a list of lines. 
		@chargeList   - A list of strings giving the charges for each section.
		@sectionStart - A list of ints giving the start index of the 
		"""

		sectionStart = []
		sectionEnd   = []
		chargeList   = []
		inputText    = []

		inputFile    = open(inputFilename, 'rb')
		nameRegex    = re.compile('^(Name)')
		prevLine     = ''

		for index, line in enumerate(inputFile):
			inputText.append(line)
			if nameRegex.match(line):
				sectionStart.append(index+1)
				chargeList.append(prevLine.strip())
				if len(sectionStart) > 1:
					sectionEnd.append(index-1)
			prevLine = line
		sectionEnd.append(index)
		return inputText, chargeList, sectionStart, sectionEnd


	def parseLine(self, inputLine):
		""" 
		Parses through the input text line and returns the 
		start position of the first character, the end position of 
		the last (non-whitespace) character and the total number of 
		non-whitespace characters. 

		@inputLine - a string giving the line to be parsed.
		"""
		startText = -1
		endText   = -1
		totalText = 0
		for index, stringChar in enumerate(inputLine):
			if stringChar != ' ' and startText == -1:
				startText = index
			elif stringChar != ' ':
				totalText += 1
				endText    = index
		return startText, endText, totalText

	def searchKeywords(self, rawInputStr):
		"""
		Returns a list of defaulters containing at least one of the provided keywords. 
		"""
		results = []
		resultSet = Set()

		# Clean up the input string
		inputStr = self.cleanString(rawInputStr)
		inputList = inputStr.split(' ')

		# Parse the input string
		for keyword in inputList:
			if keyword in self.keywordSet:
				indexList = self.keywordList[keyword]
				for index in indexList:
					resultSet.add(index)

		# Setup the final results
		finalResults = Set()

		for resultIndex in resultSet:
			defaulter       = self.defaultersList[resultIndex]
			defaulterStr    = self.cleanString(defaulter.getString())
			defaulterTokens = defaulterStr.split()
			allKeywords  = True
			for keyword in inputList:
				if keyword not in defaulterTokens:
					allKeywords = False
			if allKeywords:
				finalResults.add(resultIndex)

		for resultIndex in finalResults:
			results.append(self.defaultersList[resultIndex])

		results.sort(key=lambda x: x.getName(), reverse=False)

		return results


	def processKeywords(self):

		for index, defaulter in enumerate(self.defaultersList):

			# Build full string of name, address, profession etc.
			tokens1  = self.cleanString(defaulter.getName()).split(' ')
			tokens2  = self.cleanString(defaulter.getAddress()).split(' ')
			tokens3  = self.cleanString(defaulter.getProfession()).split(' ')
			tokens   = tokens1 + tokens2 + tokens3

			# Parse the tokens for keywords
			for keyword in tokens:
				if keyword in self.keywordSet:
					indexList = self.keywordList[keyword]
					indexList.append(index)
					self.keywordList[keyword] = indexList
				else:
					self.keywordList[keyword] = [ index ]
					self.keywordSet.add(keyword)

	def cleanString(self, inputString):
		""" 
		Clean up the input line and remove non-character codes.
		"""
		outputString = inputString.strip().lower()
		outputString = outputString.replace('  ',' ')
		outputString = outputString.replace(',',' ')
		outputString = outputString.replace('.',' ')
		outputString = outputString.replace('-',' ')
		outputString = outputString.replace('_',' ')
		outputString = outputString.replace('|',' ')
		outputString = outputString.replace('/',' ')
		outputString = outputString.replace('\\',' ')
		outputString = outputString.replace('(',' ')
		outputString = outputString.replace(')',' ')
		outputString = outputString.replace('[',' ')
		outputString = outputString.replace(']',' ')
		return outputString

	def getNumDefaulters(self):
		return len(self.defaultersList)

	def getNonWhitespace(self, line):
		wsRegex = re.compile('\s')
		total   = 0
		for char in line:
			if not wsRegex.match(char):
				total += 1
		return total

	def getCharges(self):
		return self.charges

	def isCharge(self, line):
		for charge in self.charges:
			if charge in line:
				return True
		return False

	def getCharge(self, line):
		for charge in self.charges:
			if charge in line:
				return charge
		return ''

	def listDefaulters(self):
		for defaulter in self.defaultersList:
			name    = defaulter.getName()
			address = defaulter.getAddress()
			print name, '|',  address

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

	def printSummary(self):
		profSet       = Set()
		profList      = {}
		finesList     = {}

		for defaulter in self.defaultersList:
			prof = defaulter.getProfession()
			fine = defaulter.getFine()
			if prof in profSet:
				profList[prof] += 1.0
				finesList[prof] += fine
			else:
				profList[prof] = 1.0
				finesList[prof] = fine
				profSet.add(prof)

		for prof in profSet:
			if profList[prof] > 3.0:
				print prof, profList[prof], finesList[prof]

		for defaulter in self.defaultersList:
			if defaulter.hasSentence():
				defaulter.printDetails()

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
