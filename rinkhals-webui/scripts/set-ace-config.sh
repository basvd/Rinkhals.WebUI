 #!/bin/bash
config=$1
value=$2

 cd "$(dirname "$0")"
 ./klippy-command.sh "{\"method\":\"filament_hub/set_config\",\"params\":{\"$config\":$value},\"id\":$RANDOM}" | jq -e ".result == {}"
