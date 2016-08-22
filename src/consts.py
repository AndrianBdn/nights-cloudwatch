import os 

NIGHTS_WATCH_TAG_NAME = '#NW'

NIGHTS_WATCH_ALARM_PREFIX = '#NW'

DEFAULT_METRICS = os.getenv('DEFAULT_METRICS', 'sys,ins,cpu,dsk')

NIGHTS_WATCH_SNS = os.getenv('NIGHTS_WATCH_SNS') 

REFRESH_INTERVAL_SEC = os.getenv('REFRESH_INTERVAL_SEC', 0)

AWS_REGIONS=os.getenv('AWS_REGIONS', 
	'us-east-1, us-west-1, us-west-2, eu-west-1, eu-central-1, ap-southeast-2')

