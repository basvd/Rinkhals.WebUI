#!/bin/bash
source /useremain/rinkhals/.current/tools.sh

BUILTIN_APP_PATH="$RINKHALS_ROOT/home/rinkhals/apps"
USER_APP_PATH="$RINKHALS_HOME/apps"

log() {
    local level=$1
    shift
    echo "[$level] $@"
}

toggle_app() {
    local app=$1
    local app_root=$2

    if [ -z "$app_root" ]; then
        app_root=$(get_app_root "$app")
    fi

    local enabled=$(is_app_enabled "$app" "$app_root")

    if [ ! -d "$RINKHALS_HOME/apps" ]; then
        mkdir -p "$RINKHALS_HOME/apps"
    fi

    # If this is a built-in app, handle app.enabled / app.disabled
    if [[ "$app_root" == "$BUILTIN_APP_PATH"* ]]; then
        if [ "$enabled" -eq 1 ]; then
            if [ -e "$RINKHALS_HOME/apps/$app.enabled" ]; then
                rm "$RINKHALS_HOME/apps/$app.enabled"
            fi
            touch "$RINKHALS_HOME/apps/$app.disabled"
        else
            if [ -e "$RINKHALS_HOME/apps/$app.disabled" ]; then
                rm "$RINKHALS_HOME/apps/$app.disabled"
            fi
            if [ ! -e "$app_root/.enabled" ]; then
                touch "$RINKHALS_HOME/apps/$app.enabled"
            fi
        fi
    else
        # If this is a user app, handle app/.enabled / app/.disabled
        if [ "$enabled" -eq 1 ]; then
            rm -f "$RINKHALS_HOME/apps/$app.enabled"
            rm -f "$RINKHALS_HOME/apps/$app.disabled"
            rm -f "$RINKHALS_HOME/apps/$app/.enabled"
            touch "$RINKHALS_HOME/apps/$app/.disabled"
        else
            rm -f "$RINKHALS_HOME/apps/$app.enabled"
            rm -f "$RINKHALS_HOME/apps/$app.disabled"
            rm -f "$RINKHALS_HOME/apps/$app/.disabled"
            touch "$RINKHALS_HOME/apps/$app/.enabled"
        fi
    fi

    if [ "$enabled" -eq 1 ]; then
        stop_app "$app" "$app_root"
    else
        start_app "$app" "$app_root"
    fi
}

start_app() {
    local app=$1
    local app_root=$2

    if [ -z "$app_root" ]; then
        app_root=$(get_app_root "$app")
    fi

    log "INFO" "Starting app $app from $app_root..."

    chmod +x "$app_root/app.sh"
    timeout -t 5 sh -c "$app_root/app.sh start"
    local code=$?

    if [ "$code" -ne 0 ]; then
        return
    fi

    log "INFO" "Started app $app from $app_root"
}

stop_app() {
    local app=$1
    local app_root=$2

    if [ -z "$app_root" ]; then
        app_root=$(get_app_root "$app")
    fi

    log "INFO" "Stopping app $app from $app_root..."

    chmod +x "$app_root/app.sh"
    "$app_root/app.sh" stop

    log "INFO" "Stopped app $app from $app_root"
}

get_app_root() {
    local app=$1
    local user_app_root="$USER_APP_PATH/$app"
    local builtin_app_root="$BUILTIN_APP_PATH/$app"

    if [ -e "$user_app_root" ]; then
        echo "$user_app_root"
    else
        echo "$builtin_app_root"
    fi
}

is_app_enabled() {
    local app=$1
    local app_root=$2
    if ([ -f $app_root/.enabled ] || [ -f $RINKHALS_HOME/apps/$app.enabled ]) && [ ! -f $app_root/.disabled ] && [ ! -f $RINKHALS_HOME/apps/$app.disabled ]; then
        echo 1
    else
        echo 0
    fi
}

toggle_app "$1" "$2"
