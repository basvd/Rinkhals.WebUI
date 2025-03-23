#!/bin/bash
ace_id=$1
slot=$2
material=$3
hex_color=$4

r=$(printf "%d" "0x${hex_color:1:2}")
g=$(printf "%d" "0x${hex_color:3:2}")
b=$(printf "%d" "0x${hex_color:5:2}")

cd "$(dirname "$0")"
./klippy-command.sh "{\"method\":\"filament_hub/set_filament_info\",\"params\":{\"color\":{\"B\":$b,\"G\":$g,\"R\":$r},\"id\":$ace_id,\"index\":$slot,\"type\":\"$material\"},\"id\":$RANDOM}" | jq -e ".result == {}"
