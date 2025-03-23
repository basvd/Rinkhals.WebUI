#!/bin/sh

template='
def models: {
    "20021": "Kobra 2 Pro",
    "20024": "Kobra 3",
    "20025": "Kobra S1",
};
{ html:
(if .status == "timed_out" then
"
<p><strong>The update check has timed out...</strong></p>
"
elif .status == "up_to_date" then
"
<p><strong>Your printer is up to date</strong></p>
"
elif . != null then
"
<p><strong>There is a new update for your \(models[.model_id | tostring] // "printer" )!</strong></p>
<p class=\"info\">
Version: \(.firmware_version)<br />
Release date: \(.create_date | strftime("%Y-%m-%d %H:%M:%S"))<br />
File size: \((.firmware_size / (1024 * 1024)) * 100 | round / 100 ) MB
</p>
<pre class=\"changes\">\(.update_desc)</pre>
<p><a href=\"\(.firmware_url)\">Download from Anycubic</a></p>
"
else
"<p><strong>Cannot check for update at this time...</strong></p>"
end)
}'

cd "$(dirname "$0")"
python3 ./ota-update-info.py -t 10 | jq -c "$template"
