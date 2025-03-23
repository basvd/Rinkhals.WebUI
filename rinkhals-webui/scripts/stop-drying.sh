#!/bin/bash
ace_id=$1

cd "$(dirname "$0")"
./klippy-command.sh "{\"method\":\"filament_hub/stop_drying\",\"params\":{\"id\":$1},\"id\":$RANDOM}" | jq -e ".result == {}"
