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
from optparse import OptionParser
from logging.handlers import RotatingFileHandler

class FileValidation:

	def __init__(self, inputFilename):

		reader     = self.unicodeReader(open(inputFilename, 'rU'))
		index      = 0
		prevLine   = ''
		prevTokens = []
		chargeList = []
		headerRegex = re.compile('^Name\s+Address\s+')

		for line in reader:
			if len(chargeList) == 0 and headerRegex.match(line.strip()):
				chargeList.append(prevLine)
			elif len(chargeList) > 0 and line.strip() != '':
				tokens = re.split(' {2,}', prevLine)
				print tokens
				if tokens < 3 and len(prevTokens) < 3:
					print line.strip(), index
			prevLine = line.strip()
			prevTokens = re.split(' {2,}', line.strip())
			index += 1


		print 'Processed {0} lines'.format(index)

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

class ValidLine:

	def __init__(self, inputLine, lineNum, tokens):
		self.inputLine = inputLine
		self.lineNum   = lineNum
		self.tokens    = tokens

	def getLineNum(self):
		return self.lineNum

	def getNumTokens(self):
		return len(self.tokens)


def main(argv):
	parser = OptionParser(usage="Usage: FileValidation <input-filename>")
	(options, filename) = parser.parse_args()

	if len(filename) == 1:
		if os.path.exists(filename[0]):
			validation = FileValidation(filename[0])
		else:
			parser.print_help()
			print '\nYou need to provide a file as input.'
			exit(1)
	else:
                parser.print_help()
                print '\nYou need to provide a file as input.'
                exit(1)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
