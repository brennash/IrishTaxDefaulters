import re

class Defaulter:

	def __init__(self, line):
		self.name         = ''
		self.address      = ''
		self.county       = ''
		self.profession   = ''
		self.sentence     = ''
		self.fine         = 0.0
		self.numCharges   = 0
		self.line         = line
		self.setCounties()
		self.chargeList   = []

		# Now process the names
		self.setName(line)
		self.setAddress(line)
		self.setProfession(line)

	def update(self, line):
		""" 
		Function called to append details to multi-line entries in the 
		input files. 
		"""
		nameIndexList = self.getIndex(self.name)
		addressIndexList = self.getIndex(self.address)
		professionIndexList = self.getIndex(self.profession)
		sentenceIndexList = self.getIndex(self.sentence)

		if self.getSubString(line, nameIndexList) != '':
			self.name = self.getSubString(line, nameIndexList) + ' ' + self.name
		if self.getSubString(line, addressIndexList) != '':
			self.address = self.address + ' ' + self.getSubString(line, addressIndexList)
		if self.getSubString(line, professionIndexList) != '':
			self.profession = self.profession + ' ' + self.getSubString(line, professionIndexList)

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


	def getIndex(self, searchTerm):
		try:
			startIndex = self.line.index(searchTerm)
			endIndex   = len(searchTerm) + startIndex
			return [startIndex, endIndex]
		except ValueError:
			return [-1, -1]

	def setName(self, line):
		if line is None or len(line) == 0:
			return None
		else:
			# Get position of contiguous whitespace
			if '  ' in line[0:28]:
				index = line.index('  ')
				self.name = line[0:index]
			else:
				# Otherwise find the most appropriate spacing
				indexList = self.getIndexList(line, ' ')
				validList = []
				for index in indexList:
					if index >= 4 and index <= 25:
						validList.append(index)
				self.name = line[0:validList[-1]].rstrip()

	def setAddress(self, line):

		if self.containsCounty(line):
			nameIndex       = len(self.name)
			addressStr      = line[nameIndex:].lstrip().rstrip()
			addressEndIndex = self.getCountyIndex(addressStr)
			self.address    = addressStr[0:addressEndIndex]
		elif len(self.name) == 0 and len(line) > 70:
			self.address = line[18:69].lstrip().rstrip()
		else:
			nameIndex  = len(self.name)
			addressStr = line[nameIndex:].lstrip().rstrip()

			if '  ' in addressStr[0:50]:
				tokens = addressStr.split('  ')
				self.address = tokens[0]
			else:
				indexList = self.getIndexList(addressStr, ' ')
				validList = []
				for index in indexList:
					if index >= 5 and index <= 50:
						validList.append(index)
				self.address = addressStr[0:validList[-1]].rstrip()

		for county in self.countyList:
			if county.upper() in self.address.upper():
				self.county = county.upper()


	def containsCounty(self, line):
		for county in self.countyList:
			if county in line:
				return True
		return False

	def getCountyIndex(self, line):
		for county in self.countyList:
			if county in line:
				index = line.index(county)
				index = index + len(county)
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
			,'DUBLIN 2']

	def setProfession(self, line):

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
				indexList = self.getIndexList(professionStr, ' ')
				validList = []
				for index in indexList:
					if index >= 5 and index <= 25:
						validList.append(index)
				self.profession = addressStr[0:validList[-1]].rstrip()

	def addCharge(self, charge):
		self.chargeList.append(charge)


	def getChargeList(self):
		return self.chargeList

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

	def getName(self):
		return self.name

	def getAddress(self):
		return self.address

	def getProfession(self):
		return self.profession

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
