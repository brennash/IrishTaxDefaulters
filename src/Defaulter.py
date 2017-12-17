import re
import sys
import logging

class Defaulter:

	def __init__(self, line):
		"""
		   Basic constructor for an empty Defaulter instance.
		"""

		# Setup the logging
		try:
			self.logger = logging.getLogger('__main__')
		except:
			self.logger = None

		# Setup the parameters
		self.name         = ''
		self.address      = ''
		self.county       = ''
		self.occupation   = ''
		self.sentence     = ''
		self.fineStr      = ''
		self.fine         = 0.0
		self.numCharges   = 0
		self.lines        = []
		self.chargeList   = []

		# Set the default encoding
		reload(sys)
		sys.setdefaultencoding('utf-8')

		# Add the line
		self.lines.append(line)

		# Now tokenize the line 
		tokens = re.split(' {2,20}',line)

		if len(tokens) >= 3:
			self.name       = tokens[0]
			self.address    = tokens[1]
			self.occupation = tokens[2]
		else:
			if self.logger is not None:
				self.logger.error('Cannot parse Defaulter - {0}'.format(line))

	def update(self, line):

		nameRegex           = re.compile('^[A-Z0-9]')
		tokens              = re.split(' {2,20}',line)
		if len(tokens) == 1 and nameRegex.match(line):
			self.name = self.name + ' ' + tokens[0]
		else:
			nameIndexList       = self.getIndexList(self.lines[0], self.name, 0)
			addressIndexList    = self.getIndexList(self.lines[0], self.address, nameIndexList[1])
			occupationIndexList = self.getIndexList(self.lines[0], self.occupation, addressIndexList[1])

			if nameIndexList[0] != -1:
				subString = line[nameIndexList[0]:nameIndexList[1]].strip()
				self.name = (self.name + ' ' + subString).strip()

			if addressIndexList[0] != -1:
				subString = line[addressIndexList[0]:addressIndexList[1]].strip()
				self.address = (self.address + ' ' + subString).strip()

			if occupationIndexList[0] != -1:
				subString = line[occupationIndexList[0]:occupationIndexList[1]].strip()
				self.occupation = (self.occupation + ' ' + subString).strip()

	def getIndexList(self, line, searchTerm, beginIndex):
		""" 
		Returns the start and end index of the particular term if it
		occurs in the original input line. Otherwise returns a 
		2-element array contain -1.
		"""
		try:
			if beginIndex is None or beginIndex == -1:
				return [-1, -1]
			else:
				startIndex     = line.find(searchTerm,beginIndex)
				endIndex       = startIndex + len(searchTerm)
				indexList      = [startIndex, endIndex]
				if startIndex == -1:
					return [-1, -1]
				else:
					return indexList
		except Exception, err:
			return [-1, -1]



	def getSubString(self, line, indexList):

		emptyString = re.compile('^\s+$')

		if indexList is None:
			return ''
		elif len(indexList) != 2:
			return ''
		elif indexList[0] == -1 or indexList[1] == -1:
			return ''
		else:
			startIndex = indexList[0]
			endIndex   = indexList[1]
			try:
				if startIndex != -1:
					subString = line[startIndex:endIndex]
					if emptyString.match(subString):
						return ''
					else:
						return subString.lstrip().rstrip()
				else:
					return ''
			except Exception, err:
				if self.logger is not None:
					self.logger.error('Defaulter:getSubString() - {0}'.format(err))
				return ''

	def getString(self):
		result  = '{0}, '.format(self.getName())
		result += '{0}, '.format(self.getAddress())
		result += '{0}, '.format(self.getCounty())
		result += '{0}'.format(self.getProfession())
		return result




	def setFine(self, line, lineNumber):
		""" 
		Sets the fine amount as a float value. This function requires the 
		profession to be set before the fine amount can be indexed. 
		"""
		# Only set the fine if a valid name/address/profession is already present
		if self.name != '' and self.address != '' and self.profession is not None:
			# Fine the index position of the profession in the string
			index            = line.index(self.profession)
			profLen          = len(self.profession)
			fineStr          = line[self.professionIndex[1]+1:].lstrip().rstrip()

			if '  ' in fineStr:
				tokens         = fineStr.split('  ')
				self.fineStr   = tokens[0]
				self.fine      = self.toFloat(tokens[0], lineNumber)
				startIndex     = self.line.find(self.fineStr,self.professionIndex[1])
				endIndex       = startIndex + len(self.fineStr)
				self.fineIndex = [ startIndex, endIndex ]
			else:
				indexList = self.getIndexList(fineStr, ' ')
				validList = []
				for index in indexList:
					if index >= 5 and index <= 25:
						validList.append(index)
				if len(validList) > 0:
					self.fineStr   = fineStr[0:validList[-1]].rstrip()
					self.fine      = self.toFloat(fineStr[0:validList[-1]].rstrip(), lineNumber)
					startIndex     = self.line.find(self.fineStr,self.professionIndex[1])
					endIndex       = startIndex + len(self.fine)
					self.fineIndex = [ startIndex, endIndex ]


	def setSentence(self, line, lineNumber=0):
		""" 
		Sets the sentence as a string value. This function requires the 
		fine to be set before the sentence can be indexed. 
		"""
		# Only set the fine if a valid name/address/profession is already present
		if self.name != '' and self.address != '' and self.profession is not None:
			# Fine the index position of the profession in the string
			index            = self.getIndex(self.fineStr)
			fineLen          = len(self.fineStr)
			if self.fineIndex is not None:
				sentenceStr      = line[self.fineIndex[1]+1:].lstrip().rstrip()
			else:
				sentenceStr      = line[self.professionIndex[1]+1:].lstrip().rstrip()
			charRegex        = re.compile('[a-zA-Z]+')

			if charRegex.match(sentenceStr) or 'YEARS' in sentenceStr or 'MONTHS' in sentenceStr or 'DAYS' in sentenceStr:
				if '  ' in sentenceStr:
					tokens            = sentenceStr.split('  ')
					self.sentence     = tokens[0]
					startIndex        = self.line.find(self.sentence,self.fineIndex[1])
					endIndex          = startIndex + len(self.sentence)
					self.setenceIndex = [ startIndex, endIndex ]
				else:
					indexList = self.getIndexList(sentenceStr, ' ')
					validList = []
					for index in indexList:
						if index >= 5 and index <= 25:
							validList.append(index)
					self.sentence     = sentenceStr[0:validList[-1]].rstrip()
					startIndex        = self.line.find(self.sentence,self.fineIndex[1])
					endIndex          = startIndex + len(self.sentence)
					self.setenceIndex = [ startIndex, endIndex ]
		else:
			if self.logger is not None:
				self.logger.warning('Trying to set the sentence with no name/address set')

	def setNumCharges(self, line, lineNumber=0):
		if len(line) > 0:
			tokens = line.strip().split(' ')
			if tokens[-1].isdigit():
				self.numCharges = int(tokens[-1])

	def getCounty(self):
		return self.county

	def initCounties(self):
		self.countyList = ['CO. ANTRIM'
			,'CO. ARMAGH'
			,'CO. CARLOW'
			,'CO. CAVAN'
			,'CO. CLARE'
			,'CO. CORK'
			,'CO. DERRY'
			,'CO. DONEGAL'
			,'CO. DOWN'
			,'CO. DUBLIN'
			,'CO. FERMANAGH'
			,'CO. GALWAY'
			,'CO. KERRY'
			,'CO. KILDARE'
			,'CO. KILKENNY'
			,'CO. LAOIS'
			,'CO. LEITRIM'
			,'CO. LIMERICK'
			,'CO. LONGFORD'
			,'CO. LOUTH'
			,'CO. MAYO'
			,'CO. MEATH'
			,'CO. MONAGHAN'
			,'CO. OFFALY'
			,'CO. ROSCOMMON'
			,'CO. SLIGO'
			,'CO. TIPPERARY'
			,'CO. TYRONE'
			,'CO. WATERFORD'
			,'CO. WESTMEATH'
			,'CO. WEXFORD'
			,'CO. WICKLOW'
			,'DUBLIN 3'
			,'DUBLIN 4'
			,'DUBLIN 5'
			,'DUBLIN 6'
			,'DUBLIN 7'
			,'DUBLIN 8'
			,'DUBLIN 9'
			,'DUBLIN 10'
			,'DUBLIN 11'
			,'DUBLIN 12'
			,'DUBLIN 13'
			,'DUBLIN 14'
			,'DUBLIN 15'
			,'DUBLIN 16'
			,'DUBLIN 17'
			,'DUBLIN 18'
			,'DUBLIN 20'
			,'DUBLIN 22'
			,'DUBLIN 24'
			,'DUBLIN 1'
			,'DUBLIN 2'
			,'SCOTLAND'
			,'UNITED KINGDOM'
			,'ENGLAND'
			,'WALES'
			,'ROMANIA'
			,'MOLDOVA'
			,'LATVIA'
			,'LITHUANIA'
			,'BULGARIA'
			,'ALBANIA']

	def addCharge(self, charge):
		self.chargeList.append(charge)

	def toFloat(self, strValue, lineNumber):
		""" 
		Returns a positive float value from a given string input, e.g., 6,000.00.
		"""
		try:
			floatStr = ''
			for char in strValue:
				if char.isdigit() or char == '.':
					floatStr = floatStr + char
			return float(floatStr)
		except:
			if self.logger is not None:
				self.logger.error('Error converting {0} to float on line {1}'.format(strValue, lineNumber))
			return 0.0

	def getName(self):
		return self.name

	def getAddress(self):
		return self.address

	def getFine(self):
		return self.fine

	def getOccupation(self):
		return self.occupation

	def getSentence(self):
		return self.sentence

	def getNumCharges(self):
		return self.numCharges

	def printDetails(self):
		print '{0},{1},{2},{3}'.format(self.name, self.address, self.profession, self.sentence)
