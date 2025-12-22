
import subprocess
import threading
import time
from typing import Optional
import os
import signal
from datetime import datetime
from summon_db import insert_summon

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

# ---------- Config ----------
BEDROCK_SERVER_PATH = "/home/doo/minecraft-bedrock-server/bedrock-server-1.21.131.1/bedrock_server"
API_KEY = "super-secret-test-key22"
BEDROCK_SERVER_PORT = 19132
API_PORT = 8000

# ---------- Helper: Kill old processes ----------
def kill_process_on_port(port: int):
    """Kill any process listening on a given TCP port."""
    try:
        result = subprocess.run(
            ["lsof", "-iTCP:{0}".format(port), "-sTCP:LISTEN", "-t"],
            capture_output=True,
            text=True,
            check=False
        )
        pids = [int(pid) for pid in result.stdout.split() if pid.strip().isdigit()]
        for pid in pids:
            print(f"Killing PID {pid} on port {port}")
            os.kill(pid, signal.SIGKILL)
    except Exception as e:
        print("No processes to kill on port", port, ":", e)

# ---------- Bedrock server wrapper ----------

class BedrockServer:
    def __init__(self, server_path: str):
        self.server_path = server_path
        self.proc: Optional[subprocess.Popen] = None
        self.lock = threading.Lock()
        self.last_list_output = None
        self._output_lock = threading.Lock()

    def start(self):
        # Kill any old bedrock_server processes
        self._kill_existing_servers()
        with self.lock:
            if self.proc is not None and self.proc.poll() is None:
                return  # already running
            print("Starting Bedrock server...")
            self.proc = subprocess.Popen(
                [self.server_path],
                cwd=os.path.dirname(self.server_path),  # important for server.properties
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            threading.Thread(target=self._read_output, daemon=True).start()

    def _kill_existing_servers(self):
        try:
            result = subprocess.run(
                ["pgrep", "-f", "bedrock_server"],
                capture_output=True,
                text=True,
                check=False
            )
            pids = [int(pid) for pid in result.stdout.split() if pid.strip().isdigit()]
            for pid in pids:
                print(f"Killing existing Bedrock server PID {pid}")
                os.kill(pid, signal.SIGKILL)
        except Exception as e:
            print("No existing Bedrock server processes:", e)

    def _read_output(self):
        if not self.proc or not self.proc.stdout:
            return
        capture_players = False
        player_lines = []
        for line in self.proc.stdout:
            print("[BEDROCK]", line, end="")
            # If previous line was 'players online:', capture following lines as player names
            if capture_players:
                # If the line is empty or looks like a log line, stop capturing
                if not line.strip() or line.strip().startswith("[") or ":" in line:
                    with self._output_lock:
                        self.last_list_output = ",".join(player_lines).strip()
                    capture_players = False
                    player_lines = []
                else:
                    player_lines.append(line.strip())
                continue
            if "players online:" in line:
                # Start capturing player names from next line(s)
                capture_players = True
                player_lines = []
                continue

    def send_command(self, cmd: str):
        with self.lock:
            if self.proc is None or self.proc.poll() is not None:
                raise RuntimeError("Bedrock server is not running")
            assert self.proc.stdin is not None
            self.proc.stdin.write(cmd + "\n")
            self.proc.stdin.flush()

    def get_online_players(self, timeout=5.0):
        """Send 'list' command and parse output for online players. Always return last known list if no new output."""
        with self._output_lock:
            prev_list_output = self.last_list_output
        self.send_command("list")
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(0.1)
            with self._output_lock:
                if self.last_list_output is not None and self.last_list_output != prev_list_output:
                    players = self.last_list_output
                    if players:
                        return [p.strip() for p in players.split(",") if p.strip()]
                    else:
                        return []
        # Timeout: return last known (possibly stale) list
        if prev_list_output:
            return [p.strip() for p in prev_list_output.split(",") if p.strip()]
        return []


bedrock = BedrockServer(BEDROCK_SERVER_PATH)

# ---------- FastAPI app ----------
app = FastAPI(title="NFC → Minecraft API")


class NfcEvent(BaseModel):
    token_id: str
    player: Optional[str] = None
    action: str


class SummonRequest(BaseModel):
    server_ip: str
    server_port: int
    summoned_object_type: str
    summoning_user: str
    summoned_user: str
    timestamp: Optional[str] = None  # UTC ISO format
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None

def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.on_event("startup")
def startup_event():
    # Kill old Uvicorn/API processes
    kill_process_on_port(API_PORT)
    # Start the Bedrock server
    bedrock.start()
    time.sleep(5)  # wait for server to boot



@app.post("/nfc-event")
def handle_nfc_event(event: NfcEvent, x_api_key: str = Header(...)):
    require_api_key(x_api_key)

    try:
        if event.action == "spawn_ender_dragon" and event.player:
            # spawn dragon at player's location
            cmd = f"summon ender_dragon ~ ~ ~"
        elif event.action == "give_diamond_sword" and event.player:
            cmd = f"give {event.player} diamond_sword 1"
        else:
            raise HTTPException(status_code=400, detail="Unknown action or missing player")

        bedrock.send_command(cmd)
        return {"status": "ok", "executed": cmd}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- New endpoint: Summon NPC ----------

@app.post("/summon")
def summon_npc(req: SummonRequest, x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    # Validate required fields
    if not all([req.server_ip, req.server_port, req.summoned_object_type, req.summoning_user, req.summoned_user]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    # Use provided timestamp or current UTC
    timestamp_utc = req.timestamp or datetime.utcnow().isoformat()
    # Store summon request in DB
    insert_summon(
        req.server_ip,
        req.server_port,
        req.summoned_object_type,
        req.summoning_user,
        req.summoned_user,
        timestamp_utc,
        req.gps_lat,
        req.gps_lon
    )
    # Build summon command
    cmd = f"execute as @a[name={req.summoned_user}] at @s run summon {req.summoned_object_type} ~ ~ ~2"
    try:
        bedrock.send_command(cmd)
        return {"status": "ok", "executed": cmd}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- New endpoint: List users ----------
@app.get("/users")
def get_users(x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    try:
        users = bedrock.get_online_players()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))