#!/bin/bash

template='
def fmt_seconds(s):
    "\(s / 3600 | floor):" + (s | strftime("%M:%S"));

.result.status.filament_hub.filament_hubs as $hubs | $hubs[] | {
    id: .id,
    title_no: (if ($hubs | length > 1) then "#\(.id + 1)" else "" end),
    is_drying: (.dryer_status.status != "stop"),
    html:
    ((.slots | map(
        if .status == "empty" or .status == "runout" then
        "
        <div class=\"filament\">
        <span class=\"icon\"><iconify-icon icon=\"mdi:numeric-\(.index + 1)-circle-outline\"></iconify-icon></span>
        -
        </div>
        "
        else
        "
        <div class=\"filament\">
        <span class=\"icon\"><iconify-icon icon=\"mdi:numeric-\(.index + 1)-circle\" style=\"color: rgb(\(.color | join(",")))\"></iconify-icon></span>
        \(.type)
        </div>
        "
        end
    ) | join("")) +
    "<div class=\"ace-status\">
    Status: \(.status) \(if .dryer_status.status != "stop" then ("/ " + .dryer_status.status) else "" end)<br/>
    Temperature: \(.temp)℃ (target: \(.dryer_status.target_temp)℃)<br/>
    Remaining time: <span class=\"remaining\">\(fmt_seconds(.dryer_status.remain_time))</span><br/>
    </div>
    ")
}'

cd "$(dirname "$0")"
./klippy-command.sh "{\"method\":\"objects/query\",\"params\":{\"objects\":{\"filament_hub\":null}},\"id\":$RANDOM}" | jq -c "$template"
