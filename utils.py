def listToSet(inputList):
	resultSet = set({})
	for item in inputList:
		resultSet.add(item)
	return resultSet

class BillLog:
	def __init__(self):
		self.billList = {}
		self.memberIDDict = {}
		self.members = {}