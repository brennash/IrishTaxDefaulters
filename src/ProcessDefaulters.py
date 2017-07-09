import io
import re
import os
import csv
import sys
import time
import datetime
import collections
from sets import Set
from Defaulter import Defaulter
from optparse import OptionParser


class ProcessDefaulters:

	def __init__(self):
		self.defaulterList = []

	def run(self, filename):
		""" 
		Reads the text and sets up the defaulters list
		"""
		self.readText(filename)
		self.listDefaulters()

	def readText(self, filename):
		""" 
		Read the CSV file, initialize these as defaulter objects and
		add the defaulter object to the list. 
		"""
		startRegex   = re.compile('^[A-Z-\']+[,]{1}\s+')
		extraRegex   = re.compile('^\s*[A-Z0-9-,]')

		inputFile    = open(filename, 'rb')
		for index, line in enumerate(inputFile):
			nonWSChars = self.getNonWhitespace(line)

			if nonWSChars > 50 and 'Name' not in line and startRegex.match(line):
				defaulter = Defaulter(line)
				self.defaulterList.append(defaulter)
			elif nonWSChars <= 50 and 'Name' not in line and extraRegex.match(line) and not self.isCharge(line):
				if len(self.defaulterList) > 0:
					self.defaulterList[-1].update(line)
			index += 1


	def getNonWhitespace(self, line):
		wsRegex = re.compile('\s')
		total   = 0
		for char in line:
			if not wsRegex.match(char):
				total += 1

		return total

	def isCharge(self, line):
		charges = ['ALCOHOL SMUGGLING'
			,'CIGARETTE SMUGGLING'
			,'CLAIMING VAT REPAYMENT(S) TO WHICH NOT ENTITLED'
			,'CLAIMING MEDICAL EXPENSE REPAYMENT(S) TO WHICH NOT ENTITLED'
			,'CLAIMING '
			,'DELIVERING INCORRECT INCOME TAX RETURN(S)'
			,'DELIVERING INCORRECT INCOME VAT RETURN(S)'
			,'DELIVERING INCORRECT RCT RETURN(S)'
			,'DELIVERING INCORRECT'
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
			,'FAILURE TO'
			,'FILING INCORRECT INCOME TAX RETURN(S)'
			,'ILLEGAL BETTING'
			,'ILLEGAL SELLING OF CIGARETTES'
			,'KEEPING UNTAXED TOBACCO FOR SALE'
			,'MISUSE OF MARKED MINERAL OIL'
			,'OIL LAUNDERING'
			,'OIL SMUGGLING'
			,'POSSESSION OF AN UNREGISTERED VEHICLE'
			,'POSSESSION OF COUNTERFEIT ALCOHOL FOR SALE'
			,'POSSESSION OF']

		for charge in charges:
			if charge in line:
				return True
		return False


	def listDefaulters(self):

		for defaulter in self.defaulterList:
			name    = defaulter.getName()
			address = defaulter.getAddress()
			print name, '|',  address

def main(argv):
        parser = OptionParser(usage="Usage: ProcessDefaulters <text-filename>")
        (options, filename) = parser.parse_args()

	if len(filename) == 1:
		if os.path.exists(filename[0]):
			processor = ProcessDefaulters()
			processor.run(filename[0])
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



