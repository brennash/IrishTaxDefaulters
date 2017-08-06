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

		self.logger = None

		self.charges = ['ALCOHOL SMUGGLING'
			,'CIGARETTE SMUGGLING'
			,'CLAIMING VAT REPAYMENT(S) TO WHICH NOT ENTITLED'
			,'CLAIMING MEDICAL EXPENSE REPAYMENT(S) TO WHICH NOT ENTITLED'
			,'DELIVERING INCORRECT INCOME TAX RETURN(S)'
			,'DELIVERING INCORRECT INCOME VAT RETURN(S)'
			,'DELIVERING INCORRECT RCT RETURN(S)'
			,'FAILURE TO KEEP THE VEHICLE STATIONARY'
			,'FAILURE TO HOLD CURRENT LIQUOR LICENCE'
			,'FAILURE TO DELIVER STATEMENT OF AFFAIRS'
			,'FAILURE TO LODGE INCOME TAX RETURN(S)'
			,'FAILURE TO LODGE CORPORATION TAX RETURN(S)'
			,'FAILURE TO LODGE VAT RETURN(S)'
			,'FAILURE TO LODGE P35 RETURN(S)'
			,'FAILURE TO LODGE P60 RETURN(S)'
			,'FAILURE TO REMIT VAT'
			,'FAILURE TO MAINTAIN BOOKS AND RECORDS'
			,'FAILURE TO HOLD A CURRENT LIQUOR LICENCE'
			,'FAILURE TO PRODUCE BOOKS & RECORDS'
			,'FILING INCORRECT INCOME TAX RETURN(S)'
			,'ILLEGAL BETTING'
			,'ILLEGAL SELLING OF CIGARETTES'
			,'KEEPING UNTAXED TOBACCO FOR SALE'
			,'KEEPING PROHIBITED GOODS IN A VEHICLE'
			,'MISUSE OF MARKED MINERAL OIL'
			,'OIL LAUNDERING'
			,'OIL SMUGGLING'
			,'POSSESSION OF AN UNREGISTERED VEHICLE'
			,'POSSESSION OF COUNTERFEIT ALCOHOL FOR SALE'
			,'POSSESSION OF '
			,'FAILURE TO '
			,'CLAIMING '
			,'ILLEGAL '
			,'DELIVERING INCORRECT']

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
					self.readFile(dir+os.sep+filename)

		# Try to log the output
		if self.logger is not None:
			self.logger.info('Processed {0} defaulters'.format(len(self.defaulterList)))

		# Process the keywords for indexing and lookup
		self.processKeywords()


	def searchKeywords(self, inputStr):
		"""
		Returns a list of defaulters containing at least one of the provided keywords. 
		"""
		results = []
		resultSet = Set()

		# Clean up the input string
		inputStr = inputStr.replace(',',' ')
		inputStr = inputStr.replace('.',' ')
		inputStr = inputStr.replace('-',' ')
		inputStr = inputStr.replace('_',' ')
		inputList = inputStr.split(' ')

		# Parse the input string
		for keyword in inputList:
			if keyword in self.keywordSet:
				indexList = self.keywordList[keyword]
				for index in indexList:
					resultSet.add(index)

		for resultIndex in resultSet:
			results.append(self.defaulterList[resultIndex])

		results.sort(key=lambda x: x.getName(), reverse=False)

		return results


	def run(self, filename):
		""" 
		Reads a single input data file and sets up the defaulters list
		"""
		if self.logger is not None:
			self.logger.info('Reading single input data file {0}'.format(filename))

		self.readFile(filename)
		self.listDefaulters()

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
			defaulterStr  = defaulter.getName().lower()
			defaulterStr += ' '
			defaulterStr += defaulter.getAddress().lower()
			defaulterStr += ' '
			defaulterStr += defaulter.getProfession().lower()

			# Clean up this string
			defaulterStr  = defaulterStr.replace('  ',' ')
			defaulterStr  = defaulterStr.replace(',',' ')
			defaulterStr  = defaulterStr.replace('.',' ')
			defaulterStr  = defaulterStr.replace('-',' ')
			defaulterStr  = defaulterStr.replace('_',' ')
			defaulterStr  = defaulterStr.replace('|',' ')

			# Split it into tokens
			tokens = defaulterStr.split(' ')

			# Parse the tokens for keywords
			for keyword in tokens:
				if keyword in self.keywordSet:
					indexList = self.keywordList[keyword]
					indexList.append(index)
					self.keywordList[keyword] = indexList
				else:
					self.keywordList[keyword] = [ index ]
					self.keywordSet.add(keyword)

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



