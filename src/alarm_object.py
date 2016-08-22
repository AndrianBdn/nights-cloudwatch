class AlarmObject(object):

	def name(self):
		return self.dict['AlarmName']

	def __init__(self, alarmDict):
		self.dict = alarmDict
		compare = [self.name()]
		compare += self.dict['AlarmActions']

		self.compare_string = "###".join(sorted(compare))


	def __eq__(self, other):
		return self.compare_string == other.compare_string
 
	def __hash__(self):
		return hash(self.compare_string)


	def __repr__(self):
		return "Alarm: %s" % (self.name)