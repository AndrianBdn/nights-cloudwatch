from alarm_object import AlarmObject

class AlarmDiffer():

	def __init__(self, existing_alarms, new_alarms):
		self.existing_alarms_set = set(existing_alarms)
		self.new_alarms_set = set(new_alarms)

	def delete_from_aws(self):
		return self.existing_alarms_set - self.new_alarms_set

	def append_to_aws(self):
		return self.new_alarms_set - self.existing_alarms_set


