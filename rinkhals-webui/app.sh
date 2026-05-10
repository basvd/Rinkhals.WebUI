source /useremain/rinkhals/.current/tools.sh

APP_ROOT=$(dirname $(realpath $0))
PID_FILE=$APP_ROOT/app.pid
LOG_FILE=$RINKHALS_LOGS/rinkhals-webui.log

# Check if PID file points to a live rinkhals_webui process
is_running() {
    if [ ! -f "$PID_FILE" ]; then
        return 1
    fi

    PID=$(cat "$PID_FILE")
    if [ -z "$PID" ] || [ ! -e "/proc/$PID/cmdline" ]; then
        rm -f "$PID_FILE"
        return 1
    fi

    CMDLINE=$(get_command_line $PID)
    case "$CMDLINE" in
        *rinkhals_webui*)
            return 0
            ;;
    esac

    log "Stale PID file (PID $PID is not rinkhals_webui), removing"
    rm -f "$PID_FILE"
    return 1
}

status() {
    if is_running; then
        PID=$(cat "$PID_FILE")
        report_status $APP_STATUS_STARTED "$PID" "$LOG_FILE"
    else
        report_status $APP_STATUS_STOPPED "" "$LOG_FILE"
    fi
}
start() {
    if is_running; then
        log "Rinkhals WebUI already running (PID $(cat "$PID_FILE"))"
        return
    fi

    export STATIC_DIR=$APP_ROOT/static

    cd $APP_ROOT/lib
    micropython -m rinkhals_webui >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"

    log "Started Rinkhals WebUI (PID $!)"
}
stop() {
    if ! is_running; then
        log "Rinkhals WebUI is not running"
        return
    fi

    PID=$(cat "$PID_FILE")
    kill_by_id $PID
    rm -f "$PID_FILE"

    log "Stopped Rinkhals WebUI"
}
version() {
    sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$APP_ROOT/app.json"
}

case "$1" in
    status)
        status
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    version)
        version
        ;;
    *)
        echo "Usage: $0 {status|start|stop|version}" >&2
        exit 1
        ;;
esac
