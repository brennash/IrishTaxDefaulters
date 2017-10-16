import re
import sys
import logging

class Defaulter:

	def __init__(self, line, lineNumber=0):
		""" 
		Construct the defaulter object using the line read from the
		defaulters file, and including a lineNumber for error tracking.

		Inputs
		~~~~~~
		line - A string value from the file.
		lineNumber - An int giving the line number from the file (default set to zero).
		"""

		self.name         = ''
		self.address      = ''
		self.county       = ''
		self.profession   = ''
		self.sentence     = ''
		self.fineStr      = ''
		self.fine         = 0.0
		self.numCharges   = 0
		self.line         = line
		self.chargeList   = []

		# Set the default encoding
		reload(sys)
		sys.setdefaultencoding('utf-8')

		# Setup the logging
		try:
			self.logger = logging.getLogger('__main__')
		except:
			self.logger = None

		# Create the list of counties
		self.setCounties()

		# Now process the names
		self.setName(line, lineNumber)
		self.setAddress(line, lineNumber)
		self.setProfession(line, lineNumber)
		self.setCounty(line, lineNumber)
		self.setFine(line, lineNumber)
		self.setSentence(line, lineNumber)
		self.setNumCharges(line, lineNumber)

	def update(self, line):
		""" 
		Function called to append details to multi-line entries in the 
		input files. 
		"""
		nameIndexList       = self.getIndex(self.name)
		addressIndexList    = self.getIndex(self.address)
		professionIndexList = self.getIndex(self.profession)
		fineIndexList       = self.getIndex(self.fineStr)
		sentenceIndexList   = self.getIndex(self.sentence)

		if self.getSubString(line, nameIndexList) != '':
			self.name = self.getSubString(line, nameIndexList) + ' ' + self.name
		if self.getSubString(line, addressIndexList) != '':
			self.address = self.address + ' ' + self.getSubString(line, addressIndexList)
		if self.getSubString(line, professionIndexList) != '':
			self.profession = self.profession + ' ' + self.getSubString(line, professionIndexList)
		if self.getSubString(line, fineIndexList) != '':
			self.fineStr = self.fineStr + ' ' + self.getSubString(line, fineIndexList)
		if self.getSubString(line, sentenceIndexList) != '':
			self.sentence = self.sentence + ' ' + self.getSubString(line, sentenceIndexList)

		# Re-set the county if needs be
		self.setCounty(line)

	def getSubString(self, line, indexList):

		emptyString = re.compile('^\s+$')

		if len(indexList) != 2:
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
				return ''

	def getString(self):
		result = '{0}, '.format(self.getName())
		result += '{0}, '.format(self.getAddress())
		result += '{0}, '.format(self.getCounty())
		result += '{0}'.format(self.getProfession())
		return result

	def getIndex(self, searchTerm):
		try:
			startIndex = self.line.index(searchTerm)
			endIndex   = len(searchTerm) + startIndex
			return [startIndex, endIndex]
		except ValueError:
			if self.logger is not None:
				self.logger.error('Cannot getIndex() ValueError for {0}'.format(searchTerm))
			return [-1, -1]
		except TypeError:
			if self.logger is not None:
				self.logger.error('Cannot getIndex() TypeError for {0}'.format(searchTerm))
			return [-1, -1]

	def setName(self, line, lineNumber=0):
		if line is None or len(line) == 0:
			return None
		else:
			# Get position of contiguous whitespace
			if '  ' in line[0:28]:
				index = line.index('  ')
				self.name = line[0:index].encode("utf8")
			else:
				# Otherwise find the most appropriate spacing
				indexList = self.getIndexList(line, ' ')
				validList = []
				for index in indexList:
					if index >= 4 and index <= 25:
						validList.append(index)
				self.name = line[0:validList[-1]].rstrip().encode("utf8")

	def setAddress(self, line, lineNumber=0):
		""" Sets the address of the defaulter, which is
		    typically the second column in the input data. No
		    data is returned, however, the address details are 
		    set in the address variable as a string.
		"""
		if self.containsCounty(line):
			nameIndex       = len(self.name)
			addressStr      = line[nameIndex:].lstrip().rstrip()
			addressEndIndex = self.getCountyIndex(addressStr)
			self.address    = addressStr[0:addressEndIndex].encode("utf8")
		elif len(self.name) == 0 and len(line) > 70:
			self.address = line[18:69].lstrip().rstrip().encode("utf8")
		else:
			nameIndex  = len(self.name)
			addressStr = line[nameIndex:].lstrip().rstrip()

			if '  ' in addressStr or '\t' in addressStr:
				tokens = addressStr.split('  ')
				self.address = tokens[0]
			else:
				if '  ' in addressStr[0:50]:
					tokens = addressStr.split('  ')
					self.address = tokens[0]
				else:
					indexList = self.getIndexList(addressStr, ' ')
					validList = []
					for index in indexList:
						if index >= 5 and index <= 50:
							validList.append(index)
					self.address = addressStr[0:validList[-1]].rstrip().encode("utf8")

	def setProfession(self, line, lineNumber):

		# Only set the profession if a valid name/address is already present
		if self.name != '' and self.address != '':

			# Fine the index position of the address in the string
			index            = line.index(self.address)
			addrLen          = len(self.address)
			professionStr    = line[(index+addrLen):].lstrip().rstrip()

			if '  ' in professionStr:
				tokens = professionStr.split('  ')
				self.profession = tokens[0]
			else:
				try:
					indexList = self.getIndexList(professionStr, ' ')
					validList = []
					for index in indexList:
						if index >= 5 and index <= 25:
							validList.append(index)
					self.profession = professionStr[0:validList[-1]].rstrip()
				except:
					if self.logger is not None:
						self.logger.error('Problem finding profession for {0}'.format(line))
					else:
						print line

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
			fineStr          = line[(index+profLen):].lstrip().rstrip()

			if '  ' in fineStr:
				tokens       = fineStr.split('  ')
				self.fineStr = tokens[0]
				self.fine    = self.toFloat(tokens[0], lineNumber)
			else:
				indexList = self.getIndexList(fineStr, ' ')
				validList = []
				for index in indexList:
					if index >= 5 and index <= 25:
						validList.append(index)
				if len(validList) > 0:
					self.fineStr = fineStr[0:validList[-1]].rstrip()
					self.fine    = self.toFloat(fineStr[0:validList[-1]].rstrip(), lineNumber)

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
			sentenceStr      = line[(index[0]+fineLen):].lstrip().rstrip()
			charRegex        = re.compile('[a-zA-Z]+')

			if charRegex.match(sentenceStr) or 'YEARS' in sentenceStr or 'MONTHS' in sentenceStr or 'DAYS' in sentenceStr:
				if '  ' in sentenceStr:
					tokens = sentenceStr.split('  ')
					self.sentence = tokens[0]
				else:
					indexList = self.getIndexList(sentenceStr, ' ')
					validList = []
					for index in indexList:
						if index >= 5 and index <= 25:
							validList.append(index)
					self.sentence = sentenceStr[0:validList[-1]].rstrip()
		else:
			if self.logger is not None:
				self.logger.warning('Trying to set the sentence with no name/address set')

	def setNumCharges(self, line, lineNumber=0):
		if len(line) > 0:
			tokens = line.strip().split(' ')
			if tokens[-1].isdigit():
				self.numCharges = int(tokens[-1])

	def setCounty(self, line, lineNumber=0):
		if self.county == '':
			# Iterate through the list of counties setting them
			for county in self.countyList:
				if county.upper() in self.address.upper():
					self.county = county.upper().encode("utf8")
					break

	def containsCounty(self, line):
		for county in self.countyList:
			if county in line:
				return True
		return False

	def getCounty(self):
		return self.county

	def getCountyIndex(self, line):
		for county in self.countyList:
			if county in line:
				index = line.index(county)
				index = index + len(county)
				if line[index] == '.' or line[index] == ',':
					index += 1
				return index
		return -1

	def setCounties(self):
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

	def getChargeList(self):
		return self.chargeList

	def getChargeListAsString(self):
		return ','.join(self.chargeList)

	def getStartIndex(self, line, startIndex):
		charRegex = re.compile('[a-zA-Z0-9]')
		for index, char in enumerate(line[startIndex:]):
			if charRegex.match(char):
				return (index+startIndex)
		return -1

	def getEndIndex(self, line, startIndex):
		shortLine = line[startIndex:]
		if '  ' in shortLine:
			index = shortLine.index('  ')
			return index
		else:
			return -1

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

	def getProfession(self):
		return self.profession

	def getSentence(self):
		return self.sentence

	def getNumCharges(self):
		return self.numCharges

	def hasSentence(self):
		if self.sentence is not None and len(self.sentence) > 3:
			return True
		return False

	def getIndexList(self, line, targetChar):
		""" 
		A helper function which returns the list of indexes (as a list) of a 
		particular character in a string.
		"""
		indexList = []
		for index, char in enumerate(line):
			if char == targetChar:
				indexList.append(index)	
		return indexList

	def isComplete(self):
		if self.name != '' and self.address != '' and self.profession != '':
			return True
		return False
