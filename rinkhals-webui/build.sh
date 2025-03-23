#!/bin/sh

set -e

if [[ "$(pwd)" != "/tmp/update_swu/rinkhals-webui" ]]; then
    echo "Script was not called during SWU build. Exiting"
    exit 1
fi

cd /tmp

wget -O olivetin.tar.gz https://github.com/OliveTin/OliveTin/releases/download/2025.2.21/OliveTin-linux-arm7.tar.gz
tar --strip-components=1 --skip-old-files -xvzf olivetin.tar.gz \
    -C /tmp/update_swu/rinkhals-webui \
    "OliveTin-linux-arm7/OliveTin" "OliveTin-linux-arm7/webui/"

cd /tmp/update_swu/rinkhals-webui

# mv -f ./custom-webui/*.png ./webui/
rm ./build.sh
