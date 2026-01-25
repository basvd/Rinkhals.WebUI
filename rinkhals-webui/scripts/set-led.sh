#!/bin/bash

STATE=$1
if [ "$STATE" != "1" ]; then
  STATE=0
fi

cd "$(dirname "$0")"
./klippy-command.sh '{"method":"led/set_led","params":{"S":'$STATE'},"id":37}'
