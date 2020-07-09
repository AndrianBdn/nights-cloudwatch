from consts import *
from alarm_object import AlarmObject

class AlarmGenerator:

	def __init__(self, region_name, sns_arn, instance):
		self.instance = instance
		self.region_name = region_name
		self.sns_arn = sns_arn

	def alarm_name(self, name):
		return "-".join([NIGHTS_WATCH_ALARM_PREFIX, self.instance['InstanceId'], self.instance['NameTag'], name])
	
	def alarm_with_short_name(self, name):
		if name == "cpu":
			return self.cpu()
		elif name == "sys":
			return self.system_fail_recover()
		elif name == "ins":
			return self.instance_fail_reboot()
		elif name == "dsk": 
			return self.disk_warning()
		elif name == "mem":
			return self.mem_warning()

		return None

	def cpu(self):
		return AlarmObject(dict(
			AlarmName=self.alarm_name('cpu_97_25m'),
			AlarmDescription='CPU > 97% for 25 minutes',
			ActionsEnabled=True,
			AlarmActions=[ self.sns_arn ],
			OKActions=[ self.sns_arn ],
			MetricName='CPUUtilization',
			Namespace='AWS/EC2',
			Statistic='Average',
			Dimensions=[{'Name': 'InstanceId','Value': self.instance['InstanceId']},],
			Period=300,
			EvaluationPeriods=5,
			Threshold=97.0,
			ComparisonOperator='GreaterThanOrEqualToThreshold'
		));

	def system_fail_recover(self):
		return AlarmObject(dict(
			AlarmName=self.alarm_name('sys_fail_recov'),
			AlarmDescription='Hypervisor Failed for 3 minutes',
			ActionsEnabled=True,
			AlarmActions=[ self.sns_arn, 'arn:aws:automate:%s:ec2:recover' % (self.region_name) ],
			OKActions=[ self.sns_arn ],
			MetricName='StatusCheckFailed_System',
			Namespace='AWS/EC2',
			Statistic='Maximum',
			Dimensions=[{'Name': 'InstanceId','Value': self.instance['InstanceId']},],
			Period=60,
			EvaluationPeriods=3,
			Threshold=1.0,
			ComparisonOperator='GreaterThanOrEqualToThreshold'
		));


	def instance_fail_reboot(self):
		account_id = self.instance['NetworkInterfaces'][0]['OwnerId']

		return AlarmObject(dict(
			AlarmName=self.alarm_name('inst_fail_reboot'),
			AlarmDescription='Instance Check Failed for 20 minutes',
			ActionsEnabled=True,
			AlarmActions=[ self.sns_arn, 
				'arn:aws:swf:%s:%s:action/actions/AWS_EC2.InstanceId.Reboot/1.0' %
				 (self.region_name, account_id)
			],
			OKActions=[ self.sns_arn ],
			MetricName='StatusCheckFailed_Instance',
			Namespace='AWS/EC2',
			Statistic='Maximum',
			Dimensions=[{'Name': 'InstanceId','Value': self.instance['InstanceId']},],
			Period=60,
			EvaluationPeriods=20,
			Threshold=1.0,
			ComparisonOperator='GreaterThanOrEqualToThreshold'
		));

	def disk_warning(self):
		return AlarmObject(dict(
			AlarmName=self.alarm_name('disk_90_full'),
			AlarmDescription='Disk is 90% full ',
			ActionsEnabled=True,
			AlarmActions=[ self.sns_arn ],
			OKActions=[ self.sns_arn ],
			MetricName='DiskSpaceUtilization',
			Namespace='System/Linux',
			Statistic='Minimum',
			Dimensions=[
				{'Name': 'InstanceId','Value': self.instance['InstanceId']},
				{'Name': 'Filesystem', 'Value': '/dev/nvme0n1p1'},
				{'Name': 'MountPath', 'Value': '/'}
			],
			Period=900,
			EvaluationPeriods=2,
			Threshold=90.0,
			ComparisonOperator='GreaterThanOrEqualToThreshold'
		));

	def mem_warning(self):
		# Warning, doubtful threshold
		return AlarmObject(dict(
			AlarmName=self.alarm_name('mem_90_full'),
			AlarmDescription='Memory is 90% full ',
			ActionsEnabled=True,
			AlarmActions=[ self.sns_arn ],
			OKActions=[ self.sns_arn ],
			MetricName='MemoryUtilization',
			Namespace='System/Linux',
			Statistic='Minimum',
			Dimensions=[
				{'Name': 'InstanceId','Value': self.instance['InstanceId']},
			],
			Period=900,
			EvaluationPeriods=2,
			Threshold=90.0,
			ComparisonOperator='GreaterThanOrEqualToThreshold'
		));
