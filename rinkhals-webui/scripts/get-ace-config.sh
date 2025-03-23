 #!/bin/bash

 cd "$(dirname "$0")"
 ./klippy-command.sh "{\"method\":\"filament_hub/get_config\",\"params\":{},\"id\":$RANDOM}" | jq -c ".result.auto_refill = (.result.auto_refill != 0) | .result.runout_detect = (.result.runout_detect != 0) | .result"
