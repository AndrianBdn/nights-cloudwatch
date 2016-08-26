#!/bin/sh 

NAME=andrianbdn/nights-cloudwatch

docker build -t $NAME .

docker run --rm \
	-e AWS_SECRET_ACCESS_KEY -e AWS_ACCESS_KEY_ID -e NIGHTS_WATCH_SNS_LIST \
	$NAME

