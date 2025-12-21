import subprocess
import threading
import time
from typing import Optional
import os
import signal

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
        for line in self.proc.stdout:
            print("[BEDROCK]", line, end="")

    def send_command(self, cmd: str):
        with self.lock:
            if self.proc is None or self.proc.poll() is not None:
                raise RuntimeError("Bedrock server is not running")
            assert self.proc.stdin is not None
            self.proc.stdin.write(cmd + "\n")
            self.proc.stdin.flush()


bedrock = BedrockServer(BEDROCK_SERVER_PATH)

# ---------- FastAPI app ----------
app = FastAPI(title="NFC → Minecraft API")

class NfcEvent(BaseModel):
    token_id: str
    player: Optional[str] = None
    action: str

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