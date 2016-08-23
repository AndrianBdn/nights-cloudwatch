import sys
import os 
import boto3
import logging

from alarm_object 	 import AlarmObject
from alarm_generator import AlarmGenerator
from alarm_differ 	 import AlarmDiffer
from pprint 		 import pprint, pformat
from consts 		 import *


def nights_watch_tag_filter(): 
	return [{'Name': 'tag-key', 'Values': [NIGHTS_WATCH_TAG_NAME]}]


def instances_with_nights_watch(region_name):
	client = boto3.client('ec2', region_name)
	paginator = client.get_paginator('describe_instances')
	page_iterator = paginator.paginate(Filters=nights_watch_tag_filter())
	instances = []

	for page in page_iterator:
		for reservation in page['Reservations']:
			 for instance in reservation['Instances']:
			 	for tag in instance['Tags']:
			 		if tag['Key'] == 'Name':
			 			instance['NameTag'] = tag['Value']

			 		if tag['Key'] == NIGHTS_WATCH_TAG_NAME:
			 			value = tag['Value']
			 			if value == "all":
			 				value=DEFAULT_METRICS
			 			NightsWatchTypes = map(lambda x: x.strip()[:3], value.split(','))
			 			instance['NightsWatchTypes'] = NightsWatchTypes

			 	instances.append(instance); 

	return instances 

def night_watch_alarms(region_name):
	client = boto3.client('cloudwatch', region_name=region_name)	
	paginator = client.get_paginator('describe_alarms')
	page_iterator = paginator.paginate(AlarmNamePrefix=NIGHTS_WATCH_ALARM_PREFIX);
	alarms = []

	for page in page_iterator:
		for alarm in page['MetricAlarms']:
			alarms.append(AlarmObject(alarm))

	return alarms

def sync_watch_region(logger, region_name, sns_arn):
	logger.info("starting alarm sync of %s", region_name)
	instances = instances_with_nights_watch(region_name)
	new_alarms = []

	for instance in instances:
		alarmer = AlarmGenerator(region_name, sns_arn, instance)

		for nw_type in instance['NightsWatchTypes']:
			alarm = alarmer.alarm_with_short_name(nw_type)
			if alarm:
				new_alarms.append(alarm) 

		
	existing_alarms = night_watch_alarms(region_name)

	differ = AlarmDiffer(existing_alarms, new_alarms)
	update_aws(logger, region_name, differ.delete_from_aws(), differ.append_to_aws())

	logger.info("done with %s", region_name)


def update_aws(logger, region_name, alarms_delete, alarms_append):
	client = boto3.client('cloudwatch', region_name=region_name)	
	
	for alarm in alarms_append:
	 	logger.info("creating alarm %s", alarm.name())
	 	aws_log_response(logger, client.put_metric_alarm(**alarm.dict))

	if len(alarms_delete) > 0:
		delete_alarm_names = list(map(lambda x: x.name(), alarms_delete))
		logger.info("deleteing alarms %s", delete_alarm_names) 
		aws_log_response(logger, client.delete_alarms(AlarmNames = delete_alarm_names))


def aws_log_response(logger, response_dict):
	if "Error" in response_dict:
		logger.error("AWS Error: %s", response_dict['Error'])
	
	resp_meta = response_dict.get("ResponseMetadata")
	if resp_meta and resp_meta.get("HTTPStatusCode", "0") // 100 == 2: 
		logger.info("Request succeeded %d", resp_meta['HTTPStatusCode'])
		return 

	logger.error("Unknown response %s %s", resp_meta, response_dict)


def print_alarms(region_name):
	client = boto3.client('cloudwatch', region_name=region_name)	
	paginator = client.get_paginator('describe_alarms')
	page_iterator = paginator.paginate();

	for page in page_iterator:
		for alarm in page['MetricAlarms']:
			pprint(alarm)

def comma_space_to_array(input_string):
	return map(lambda x: x.strip(), input_string.split(","))

def setup_stdout_logger():
	log = logging.getLogger(__name__)
	out_hdlr = logging.StreamHandler(sys.stdout)
	out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
	out_hdlr.setLevel(logging.INFO)
	log.addHandler(out_hdlr)
	log.setLevel(logging.INFO)
	return log 

def region_sns_dict(sns_list):
	region_sns = dict()
	for sns_arn in sns_list:
		arn_pcs = sns_arn.split(":")
		arn_head = ":".join(arn_pcs[:3])
		if arn_head == 'arn:aws:sns':
			region_sns[arn_pcs[4]] = sns_arn
	return region_sns

def main():
	logger = setup_stdout_logger()

	if NIGHTS_WATCH_SNS_LIST is None:
		print("No NIGHTS_WATCH_SNS_LIST set in consts.py or env variables")
		sys.exit(1)

	regions_sns = region_sns_dict(comma_space_to_array(NIGHTS_WATCH_SNS_LIST))

	for region, sns_arn in regions.items():
		sync_watch_region(logger, region, sns_arn);


if __name__ == "__main__":
	main()

