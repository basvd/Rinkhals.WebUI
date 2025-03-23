#!/bin/bash
ace_id=$1
duration=$2
temp=$3

cd "$(dirname "$0")"
./klippy-command.sh "{\"method\":\"filament_hub/start_drying\",\"params\":{\"duration\":$duration,\"fan_speed\":0,\"id\":$ace_id,\"temp\":$temp},\"id\":$RANDOM}" | jq -e ".result == {}"
