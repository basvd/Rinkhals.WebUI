#!/bin/bash
source /useremain/rinkhals/.current/tools.sh

BUILTIN_APPS=$(find $RINKHALS_ROOT/home/rinkhals/apps -type d -mindepth 1 -maxdepth 1 -exec basename {} \; 2> /dev/null)
USER_APPS=$(find $RINKHALS_HOME/apps -type d -mindepth 1 -maxdepth 1 -exec basename {} \; 2> /dev/null)

APPS=$(printf "$BUILTIN_APPS\n$USER_APPS" | sort -uV)

SKIP_APPS=("example")

log() {
    echo "$1" >&2
}

JSON_OUTPUT=""
for APP in $APPS; do
    if [[ " ${SKIP_APPS[@]} " =~ " ${APP} " ]]; then
        log "Skipping $APP because it is in the skip list"
        continue
    fi

    BUILTIN_APP_ROOT=$(ls -d1 $RINKHALS_ROOT/home/rinkhals/apps/$APP 2> /dev/null)
    USER_APP_ROOT=$(ls -d1 $RINKHALS_HOME/apps/$APP 2> /dev/null)

    APP_ROOT=${USER_APP_ROOT:-${BUILTIN_APP_ROOT}}

    if [ ! -f $APP_ROOT/app.sh ] || [ ! -f $APP_ROOT/app.json ]; then
        continue
    fi

    APP_SCHEMA_VERSION=$(cat $APP_ROOT/app.json | sed 's/\/\/.*$//' | jq -r '.["$version"]')
    if [ "$APP_SCHEMA_VERSION" != "1" ]; then
        log "Skipping $APP ($APP_ROOT) as it is not compatible with this version of Rinkhals"
        continue
    fi

    cd $APP_ROOT
    chmod +x $APP_ROOT/app.sh

    # Check if app is enabled
    if ([ -f $APP_ROOT/.enabled ] || [ -f $RINKHALS_HOME/apps/$APP.enabled ]) && [ ! -f $APP_ROOT/.disabled ] && [ ! -f $RINKHALS_HOME/apps/$APP.disabled ]; then
        ENABLED=true
    else
        ENABLED=false
    fi

    # Read info from app.json
    # APP_INFO=$(cat $APP_ROOT/app.json)
    APP_NAME=$(jq -r '.name' $APP_ROOT/app.json)
    APP_DESCRIPTION=$(jq -r '.description' $APP_ROOT/app.json)
    APP_VERSION=$(jq -r '.version' $APP_ROOT/app.json)

    APP_STATUS=$($APP_ROOT/app.sh status | grep Status | awk '{print $2}')

    # Prepare a JSON object for the current app
    APP_JSON=$(jq -c -n \
    --arg enabled "$ENABLED" \
    --arg name "$APP_NAME" \
    --arg description "$APP_DESCRIPTION" \
    --arg version "$APP_VERSION" \
    --arg status "$APP_STATUS" \
    --arg app "$APP" \
    --arg approot "$APP_ROOT" \
    '{
        enabled: ($enabled == "true"),
        name: $name,
        description: $description,
        version: $version,
        status: $status,
        app: $app,
        approot: $approot
    }')

    # JSON_OUTPUT=$(echo "$JSON_OUTPUT" | jq ". += [$APP_JSON]")
    JSON_OUTPUT+="$APP_JSON"$'\n'
done

echo "$JSON_OUTPUT" # > apps_info.json
