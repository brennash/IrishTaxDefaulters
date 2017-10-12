import io
import re
import os
import csv
import sys
import time
import logging
import datetime
import collections
from sets import Set
from Defaulter import Defaulter
from optparse import OptionParser


class ProcessDefaulters:

	def __init__(self):

		self.keywordList   = {}
		self.keywordSet    = Set()
		self.defaulterList = []
		self.logger        = None

	def setupLogging(self):
		""" 
		Sets up the logging, inheriting the logger functionality from 
		the Defaulters Dashboard Flask application, which will be the parent/calling
		class. The logger is a rotating file logger.
		"""
		try:
			self.logger = logging.getLogger('DefaultersDashboard')
		except Exception, err:
			print err
			self.logger = None

	def loadFiles(self, dir):
		"""
		Recursively parses through a provided input data folder, extracting 
		and reading all the input files therein. 
		"""

		# Start the logger
		self.setupLogging()

		# Parse the folder for the files
		for root, dirs, files in os.walk(dir):
			path = root.split(os.sep)
			for filename in files:
				if filename[-4:] == '.txt':
					if self.logger is not None:
						self.logger.info('Reading input data file {0}'.format(filename))
					else:
						print 'Reading input data file -- {0}'.format(filename)
						self.processFile(path+os.sep+filename)

		# Try to log the output
		if self.logger is not None:
			self.logger.info('Processed {0} defaulters'.format(len(self.defaulterList)))

		# Process the keywords for indexing and lookup
		self.processKeywords()



	def processFile(self, inputFilename):

		sectionStart = []
		sectionEnd   = []
		charges      = []
		inputText    = []
		inputFile    = open(inputFilename, 'rb')
		nameRegex    = re.compile('^Name')

		# Get the section indexes and the charges
		prevLine = ''
		for index, line in enumerate(inputFile):
			inputText.append(line)
			if nameRegex.match(line):
				sectionStart.append(index+1)
				charges.append(prevLine.strip())
				if len(sectionStart) > 1:
					sectionEnd.append(index-1)
			prevLine = line
		sectionEnd.append(index)

		print sectionStart, sectionEnd
		print charges

		# Parse through it again to separate out the defaulters
		sectionIndex = 0
		startIndex   = sectionStart[sectionIndex]
		endIndex     = sectionEnd[sectionIndex]
		sectionLines = []
		sections     = []

		for index, line in enumerate(inputText):
			if index >= sectionStart[-1] and index < sectionEnd[-1]:
				print line


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
			defaulter       = self.defaulterList[resultIndex]
			defaulterStr    = self.cleanString(defaulter.getString())
			defaulterTokens = defaulterStr.split()
			allKeywords  = True
			for keyword in inputList:
				if keyword not in defaulterTokens:
					allKeywords = False
			if allKeywords:
				finalResults.add(resultIndex)

		for resultIndex in finalResults:
			results.append(self.defaulterList[resultIndex])

		results.sort(key=lambda x: x.getName(), reverse=False)

		return results

	def run(self, filename):
		""" 
		Reads a single input data file and sets up the defaulters list
		"""
		if self.logger is not None:
			self.logger.info('Reading single input data file {0}'.format(filename))

		self.processFile(filename)
		#self.listDefaulters()

	def readFile(self, filename):
		""" 
		Read the CSV file, initialize these as defaulter objects and
		add the defaulter object to the list. 
		"""
		startRegex   = re.compile('^[A-Z-\']+[,]{1}\s+')
		extraRegex   = re.compile('^\s*[A-Z0-9-,]')
		inputFile    = open(filename, 'rb')
		charge       = ''

		for index, line in enumerate(inputFile):

			if self.isCharge(line):
				charge = self.getCharge(line)

			nonWSChars = self.getNonWhitespace(line)

			if nonWSChars > 50 and 'Name' not in line and startRegex.match(line):
				defaulter = Defaulter(line)
				defaulter.addCharge(charge)
				self.defaulterList.append(defaulter)
			elif nonWSChars <= 50 and 'Name' not in line and extraRegex.match(line) and not self.isCharge(line):
				if len(self.defaulterList) > 0:
					self.defaulterList[-1].update(line)
			index += 1


	def processKeywords(self):

		for index, defaulter in enumerate(self.defaulterList):

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
		return len(self.defaulterList)

	def getNonWhitespace(self, line):
		wsRegex = re.compile('\s')
		total   = 0
		for char in line:
			if not wsRegex.match(char):
				total += 1
		return total

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
		for defaulter in self.defaulterList:
			name    = defaulter.getName()
			address = defaulter.getAddress()
			print name, '|',  address

	def getDefaulter(self, name):
		tokens = name.upper().replace(',',' ').split(' ')
		for defaulter in self.defaulterList:
			result = True
			for token in tokens:
				if token not in defaulter.getName():
					result = False
			if result:
				return defaulter
		return None

def main(argv):
        parser = OptionParser(usage="Usage: ProcessDefaulters <text-filename>")
        (options, filename) = parser.parse_args()

	if len(filename) == 1:
		if os.path.exists(filename[0]):
			if os.path.isfile(filename[0]):
				processor = ProcessDefaulters()
				processor.run(filename[0])
			elif os.path.isdir(filename[0]):
				processor = ProcessDefaulters()
				processor.loadFiles(filename[0])
			else:
		                parser.print_help()
        		        print '\nYou need to provide an existing input file.'
				exit(1)
		else:
	                parser.print_help()
        	        print '\nYou need to provide an existing input file.'
			exit(1)
	else:
                parser.print_help()
                print '\nYou need to provide existing input file.'
                exit(1)

if __name__ == "__main__":
    sys.exit(main(sys.argv))



