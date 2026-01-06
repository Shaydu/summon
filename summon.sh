
#!/bin/bash
# summon.sh - Manage Summon API and Minecraft Bedrock Server

VENVDIR="venv"
PIDFILE="summon_api_v3.pid"
WEB_PIDFILE="web/webserver.pid"
WEB_LOGFILE="logs/web.log"
WEB_APP="web/website.py"
start_web() {
    if [ -f "$WEB_PIDFILE" ]; then
        if kill -0 $(cat "$WEB_PIDFILE") 2>/dev/null; then
            echo "Web server is already running (PID $(cat $WEB_PIDFILE))"
            return 0
        else
            echo "Stale PID file found for web server. Removing..."
            rm -f "$WEB_PIDFILE"
        fi
    fi
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "Activating venv for web..."
        source "$VENVDIR/bin/activate"
    else
        echo "venv already active: $VIRTUAL_ENV"
    fi
    echo "Starting Flask web server (website.py) on 0.0.0.0:8080..."
    nohup "$VENVDIR/bin/python" "$WEB_APP" > "$WEB_LOGFILE" 2>&1 &
    echo $! > "$WEB_PIDFILE"
    echo "Started web server with PID $!"
    sleep 1
    echo "Web server started and running in background. See $WEB_LOGFILE for output."
}

stop_web() {
    if [ -f "$WEB_PIDFILE" ] && kill -0 $(cat "$WEB_PIDFILE") 2>/dev/null; then
        echo "Stopping web server (PID $(cat $WEB_PIDFILE))..."
        kill $(cat "$WEB_PIDFILE") && rm -f "$WEB_PIDFILE"
        echo "Stopped web server."
    else
        echo "Web server is not running."
    fi
}

status_web() {
    if [ -f "$WEB_PIDFILE" ] && kill -0 $(cat "$WEB_PIDFILE") 2>/dev/null; then
        echo "Web server is running (PID $(cat $WEB_PIDFILE))"
    else
        echo "Web server is not running."
    fi
}

restart_web() {
    stop_web
    sleep 1
    start_web
}
LOGFILE="logs/api.log"
APP="nfc_api.py"
PYTHON="python3"
MINECRAFT_DIR="../bedrock-server-1.21.131.1"
MINECRAFT_CMD="./bedrock_server"
MINECRAFT_SCREEN_NAME="minecraft_server"

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
    - API log: logs/api.log
    - Minecraft log: ../bedrock-server-1.21.131.1/bedrock_server.log
EOF
}

start() {
    if [ -f "$PIDFILE" ]; then
        if kill -0 $(cat "$PIDFILE") 2>/dev/null; then
            echo "Summon API is already running (PID $(cat $PIDFILE))"
            exit 0
        else
            echo "Stale PID file found for Summon API. Removing..."
            rm -f "$PIDFILE"
        fi
    fi
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "Activating venv..."
        source "$VENVDIR/bin/activate"
    else
        echo "venv already active: $VIRTUAL_ENV"
    fi
    echo "Starting Summon API (FastAPI, nfc_api.py) on 0.0.0.0:8000..."
    nohup uvicorn nfc_api:app --host 0.0.0.0 --port 8000 > "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    echo "Started Summon API with PID $!"
    sleep 1
    echo "Summon API started and running in background. See $LOGFILE for output."
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
        # Ensure venv is active before starting
        if [ -z "$VIRTUAL_ENV" ]; then
            echo "Activating venv..."
            source "$VENVDIR/bin/activate"
        else
            echo "venv already active: $VIRTUAL_ENV"
        fi
        start
    }

    start_minecraft() {
        if ! command -v screen &> /dev/null; then
            echo "Error: 'screen' is not installed. Please install it to use this feature."
            exit 1
        fi
        if screen -list | grep -q "$MINECRAFT_SCREEN_NAME"; then
            echo "Minecraft server is already running in a screen session named '$MINECRAFT_SCREEN_NAME'"
            return 0
        fi
        echo "Starting Minecraft Bedrock server in a detached screen session..."
        cd "$MINECRAFT_DIR"
        screen -dmS "$MINECRAFT_SCREEN_NAME" $MINECRAFT_CMD
        echo "Started Minecraft server in screen session '$MINECRAFT_SCREEN_NAME'"
        echo "To attach: screen -r $MINECRAFT_SCREEN_NAME"
        echo "To list screens: screen -ls"
        cd - > /dev/null
    }

    stop_minecraft() {
        if screen -list | grep -q "$MINECRAFT_SCREEN_NAME"; then
            echo "Stopping Minecraft server in screen session '$MINECRAFT_SCREEN_NAME'..."
            screen -S "$MINECRAFT_SCREEN_NAME" -X quit
            # Wait for the screen session to fully terminate
            for i in {1..10}; do
                sleep 0.5
                if ! screen -list | grep -q "$MINECRAFT_SCREEN_NAME"; then
                    break
                fi
            done
            echo "Stopped."
        else
            echo "Minecraft server is not running in a screen session."
        fi
        # Check for any lingering bedrock_server processes and kill them
        BEDROCK_PIDS=$(pgrep -f "$MINECRAFT_CMD")
        if [ -n "$BEDROCK_PIDS" ]; then
            echo "Killing leftover bedrock_server processes: $BEDROCK_PIDS"
            kill -9 $BEDROCK_PIDS
        fi
        # Check if ports 19132 or 19133 are still in use and warn
        for port in 19132 19133; do
            if lsof -i :$port | grep -q LISTEN; then
                echo "Warning: Port $port is still in use after stopping."
            fi
        done
    }

    status_minecraft() {
        if screen -list | grep -q "$MINECRAFT_SCREEN_NAME"; then
            echo "Minecraft server is running in screen session '$MINECRAFT_SCREEN_NAME'"
            screen -ls | grep "$MINECRAFT_SCREEN_NAME"
        else
            echo "Minecraft server is not running."
        fi
    }

    restart_minecraft() {
        screen -wipe > /dev/null 2>&1
        stop_minecraft
        sleep 1
        start_minecraft
    }

    start_all() {
        start_minecraft
        sleep 2
        # Ensure venv is active before starting
        if [ -z "$VIRTUAL_ENV" ]; then
            echo "Activating venv..."
            source "$VENVDIR/bin/activate"
        else
            echo "venv already active: $VIRTUAL_ENV"
        fi
        start
    }

    restart_all() {
        screen -wipe > /dev/null 2>&1
        stop
        stop_minecraft
        sleep 2
        start_minecraft
        sleep 2
        # Ensure venv is active before starting
        if [ -z "$VIRTUAL_ENV" ]; then
            echo "Activating venv..."
            source "$VENVDIR/bin/activate"
        else
            echo "venv already active: $VIRTUAL_ENV"
        fi
        start
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

    case "$1" in
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
        start-web)
            start_web
            ;;
        stop-web)
            stop_web
            ;;
        restart-web)
            restart_web
            ;;
        status-web)
            status_web
            ;;
        start-all)
            start_minecraft
            sleep 2
            if [ -z "$VIRTUAL_ENV" ]; then
                echo "Activating venv..."
                source "$VENVDIR/bin/activate"
            else
                echo "venv already active: $VIRTUAL_ENV"
            fi
            start
            start_web
            ;;
        restart-all)
            screen -wipe > /dev/null 2>&1
            stop
            stop_minecraft
            stop_web
            sleep 2
            start_minecraft
            sleep 2
            if [ -z "$VIRTUAL_ENV" ]; then
                echo "Activating venv..."
                source "$VENVDIR/bin/activate"
            else
                echo "venv already active: $VIRTUAL_ENV"
            fi
            start
            start_web
            ;;
        status-all)
            echo "--- Summon API v3 Status ---"
            status
            echo "API log: $LOGFILE"
            echo
            echo "--- Web Server Status ---"
            status_web
            echo "Web log: $WEB_LOGFILE"
            echo
            echo "--- Minecraft Server Status ---"
            status_minecraft
            echo "Minecraft log: $MINECRAFT_DIR/bedrock_server.log"
            ;;
        help)
            help
            ;;
        *)
            help
            ;;
    esac
