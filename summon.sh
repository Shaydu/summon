help() {
        cat <<EOF
summon.sh - Manage Summon API and Minecraft Bedrock Server

Usage: ./summon.sh <command>

Commands:
    start             Start the Summon API (with venv, tails API log)
    stop              Stop the Summon API
    restart           Restart the Summon API
    status            Show status of the Summon API
    start-minecraft   Start Minecraft server in a named screen session
    stop-minecraft    Stop the Minecraft server (screen session)
    restart-minecraft Restart the Minecraft server
    status-minecraft  Show status of the Minecraft server
    start-all         Start both Minecraft and Summon API
    restart-all       Restart both Minecraft and Summon API
    status-all        Show status for both servers and log locations
    help              Show this help message

Notes:
    - To connect to the Minecraft console: screen -r minecraft_server
    - To list screen sessions: screen -ls
    - API log: logs/api_sync_v3.log
    - Minecraft log: ../bedrock-server-1.21.131.1/bedrock_server.log
EOF
}
status_all() {
    echo "--- Summon API v3 Status ---"
    status
    echo "API log: $LOGFILE"
    echo
    echo "--- Minecraft Server Status ---"
    status_minecraft
    echo "Minecraft log: $MINECRAFT_DIR/bedrock_server.log"
}
restart_all() {
    stop
    stop_minecraft
    sleep 2
    start_minecraft
    sleep 2
    start
}
stop_minecraft() {
    if [ -f "$MINECRAFT_DIR/$MINECRAFT_PIDFILE" ] && kill -0 $(cat "$MINECRAFT_DIR/$MINECRAFT_PIDFILE") 2>/dev/null; then
        echo "Stopping Minecraft server (PID $(cat $MINECRAFT_DIR/$MINECRAFT_PIDFILE))..."
        kill $(cat "$MINECRAFT_DIR/$MINECRAFT_PIDFILE") && rm -f "$MINECRAFT_DIR/$MINECRAFT_PIDFILE"
        echo "Stopped."
    else
        echo "Minecraft server is not running."
    fi
}

status_minecraft() {
    if [ -f "$MINECRAFT_DIR/$MINECRAFT_PIDFILE" ] && kill -0 $(cat "$MINECRAFT_DIR/$MINECRAFT_PIDFILE") 2>/dev/null; then
        echo "Minecraft server is running (PID $(cat $MINECRAFT_DIR/$MINECRAFT_PIDFILE))"
    else
        echo "Minecraft server is not running."
    fi
}

restart_minecraft() {
    stop_minecraft
    sleep 1
    start_minecraft
}

start_all() {
    start_minecraft
    sleep 2
    start
}
#!/bin/bash
# summon.sh - Start/stop the Summon API v3 Flask service
# Usage: ./summon.sh start|stop|restart|status


VENVDIR="venv"
PIDFILE="summon_api_v3.pid"
LOGFILE="logs/api_sync_v3.log"
APP="api_sync_v3.py"
MINECRAFT_CMD="./bedrock_server"
MINECRAFT_SCREEN_NAME="minecraft_server"
MINECRAFT_DIR="../bedrock-server-1.21.131.1"
MINECRAFT_CMD="./bedrock_server"
MINECRAFT_PIDFILE="minecraft_server.pid"


start() {
    # Check if screen is installed
    if ! command -v screen &> /dev/null; then
        echo "Error: 'screen' is not installed. Please install it to use this feature."
        exit 1
    fi
    # Check if already running
    if screen -list | grep -q "$MINECRAFT_SCREEN_NAME"; then
        echo "Minecraft server is already running in a screen session named '$MINECRAFT_SCREEN_NAME'"
        exit 0
    fi
    echo "Starting Minecraft Bedrock server in a detached screen session..."
    cd "$MINECRAFT_DIR"
    screen -dmS "$MINECRAFT_SCREEN_NAME" $MINECRAFT_CMD
    echo "Started Minecraft server in screen session '$MINECRAFT_SCREEN_NAME'"
    echo "To attach: screen -r $MINECRAFT_SCREEN_NAME"
    echo "To list screens: screen -ls"
    cd - > /dev/null
    echo "Starting Summon API v3..."
    nohup $PYTHON $APP > "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    echo "Started Summon API v3 with PID $!"
    sleep 1
    echo "Tailing API log (Ctrl+C to stop tailing, API keeps running)..."
    tail -f "$LOGFILE"
}

start_minecraft() {
    if [ -f "$MINECRAFT_DIR/$MINECRAFT_PIDFILE" ] && kill -0 $(cat "$MINECRAFT_DIR/$MINECRAFT_PIDFILE") 2>/dev/null; then
        echo "Minecraft server is already running (PID $(cat $MINECRAFT_DIR/$MINECRAFT_PIDFILE))"
        exit 0
    fi
    echo "Starting Minecraft Bedrock server..."
    cd "$MINECRAFT_DIR"
    nohup $MINECRAFT_CMD > bedrock_server.log 2>&1 &
    echo $! > "$MINECRAFT_PIDFILE"
    echo "Started Minecraft server with PID $!"
    cd - > /dev/null
}

stop() {
    if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
        echo "Stopping Summon API v3 (PID $(cat $PIDFILE))..."
        kill $(cat "$PIDFILE") && rm -f "$PIDFILE"
        echo "Stopped."
    else
        echo "Summon API v3 is not running."
    fi
}

status() {
    if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
        echo "Summon API v3 is running (PID $(cat $PIDFILE))"
    else
        echo "Summon API v3 is not running."
    fi
}

restart() {
    stop
    sleep 1
    start
}

case "$1" in
                help)
                    help
                    ;;
            status-all)
                status_all
                ;;
        restart-all)
            restart_all
            ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    start-minecraft)
        start_minecraft
        ;;
    stop-minecraft)
        stop_minecraft
        ;;
    restart-minecraft)
        restart_minecraft
        ;;
    status-minecraft)
        status_minecraft
        ;;
    start-all)
        start_all
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|start-minecraft|stop-minecraft|restart-minecraft|status-minecraft|start-all}"
        exit 1
        ;;
esac
