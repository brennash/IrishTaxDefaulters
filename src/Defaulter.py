import re
import sys
import logging

class Defaulter:

	def __init__(self):
		"""
		   Basic constructor for an empty Defaulter instance.
		"""

		self.name         = ''
		self.address      = ''
		self.county       = ''
		self.profession   = ''
		self.sentence     = ''
		self.fineStr      = ''
		self.fine         = 0.0
		self.numCharges   = 0
		self.lines        = []
		self.chargeList   = []

		# Used to index the postion of each 
		# element in the line.
		self.nameIndex       = []
		self.addressIndex    = []
		self.professionIndex = []
		self.sentenceIndex   = []
		self.fineIndex       = []
		self.numChargesIndex = []

		# Set the default encoding
		reload(sys)
		sys.setdefaultencoding('utf-8')

		# Setup the logging
		try:
			self.logger = logging.getLogger('__main__')
		except:
			self.logger = None

	def addLine(self, line):

		try:
			if len(self.lines) == 0:
				# Add the line to the list of lines
				self.lines.append(line.strip())

				# Now tokenize the line 
				tokens          = re.split(' {2}',line)

				if len(tokens) >= 3:
					self.name       = tokens[0]
					self.address    = tokens[1]
					self.occupation = tokens[2]
					print 'Name',self.name,' Address',self.address,' Occupation',self.occupation
			else:
				tokens       = re.split(' {2,}',line)
				
		except Exception, err:
			print line, err
			exit(1)


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

	def getIndex(self, line, searchTerm, beginIndex):
		""" 
		Returns the start and end index of the particular term if it
		occurs in the original input line. Otherwise returns a 
		2-element array contain -1.
		"""
		try:
			startIndex     = line.find(searchTerm,beginIndex)
			endIndex       = startIndex + len(searchTerm)
			indexList      = [startIndex, endIndex]
			if startIndex == -1:
				return [-1, -1]
			else:
				return indexList
		except Exception, err:
			return [-1, -1]

	def setName(self, line, lineNumber=0):
		if line is None or len(line) == 0:
			return None
		else:
			# Get position of contiguous whitespace
			if '  ' in line[0:28]:
				index = line.index('  ')
				self.name = line[0:index].encode("utf8")
				self.nameIndex = [0, index]
			else:
				# Otherwise find the most appropriate spacing
				indexList = self.getIndexList(line, ' ')
				validList = []
				for index in indexList:
					if index >= 4 and index <= 25:
						validList.append(index)
				self.name      = line[0:validList[-1]].rstrip().encode("utf8")
				self.nameIndex = [0, validList[-1]]

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

			startIndex      = self.line.find(self.address,self.nameIndex[1])
			endIndex        = startIndex + len(self.address)
			self.addressIndex = [ startIndex, endIndex ]

		elif len(self.name) == 0 and len(line) > 70:
			self.address = line[18:69].lstrip().rstrip().encode("utf8")

			startIndex      = self.line.find(self.address,self.nameIndex[1])
			endIndex        = startIndex + len(self.addresS)
			self.addressIndex = [ startIndex, endIndex ]
		else:
			nameIndex  = len(self.name)
			addressStr = line[nameIndex:].lstrip().rstrip()

			if '  ' in addressStr or '\t' in addressStr:
				tokens            = addressStr.split('  ')
				self.address      = tokens[0]
				startIndex        = self.line.find(self.address,self.nameIndex[1])
				endIndex          = startIndex + len(self.address)
				self.addressIndex = [ startIndex, endIndex ]
			else:
				if '  ' in addressStr[0:50]:
					tokens       = addressStr.split('  ')
					self.address = tokens[0]
					startIndex        = self.line.find(self.address,self.nameIndex[1])
					endIndex          = startIndex + len(self.address)
					self.addressIndex = [ startIndex, endIndex ]
				else:
					indexList    = self.getIndexList(addressStr, ' ')
					validList    = []
					for index in indexList:
						if index >= 5 and index <= 50:
							validList.append(index)
					self.address      = addressStr[0:validList[-1]].rstrip().encode("utf8")
					startIndex        = self.line.find(self.address,self.nameIndex[1])
					endIndex          = startIndex + len(self.addresS)
					self.addressIndex = [ startIndex, endIndex ]


	def setProfession(self, line, lineNumber):

		# Only set the profession if a valid name/address is already present
		if self.name != '' and self.address != '':

			# Fine the index position of the address in the string
			index            = line.index(self.address)
			addrLen          = len(self.address)
			professionStr    = line[self.addressIndex[1]+1:].lstrip().rstrip()

			if '  ' in professionStr:
				tokens = professionStr.split('  ')
				self.profession      = tokens[0]
				startIndex           = self.line.find(self.profession,self.addressIndex[1])
				endIndex             = startIndex + len(self.profession)
				self.professionIndex = [ startIndex, endIndex ]
			else:
				try:
					indexList = self.getIndexList(professionStr, ' ')
					validList = []
					for index in indexList:
						if index >= 5 and index <= 25:
							validList.append(index)
					self.profession = professionStr[0:validList[-1]].rstrip()
					startIndex           = self.line.find(self.profession,self.addressIndex[1])
					endIndex             = startIndex + len(self.profession)
					self.professionIndex = [ startIndex, endIndex ]
				except:
					if self.logger is not None:
						self.logger.error('Problem finding profession for {0}'.format(line))


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

	def getNameIndex(self):
		return self.nameIndex

	def getProfessionIndex(self):
		return self.professionIndex

	def printDetails(self):
		print '{0},{1},{2},{3}'.format(self.name, self.address, self.profession, self.sentence)
