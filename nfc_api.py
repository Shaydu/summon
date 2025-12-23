
# --- Modular FastAPI app (v3.4) ---
from fastapi import FastAPI, HTTPException, Header, Request
from services.summon_service import handle_summon
from fastapi.responses import JSONResponse
from services.player_service import get_players as get_players_service
from services.nfc_service import handle_nfc_event as handle_nfc_event_service

app = FastAPI(title="NFC → Minecraft API v3.4")

API_KEY = "super-secret-test-key22"

def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

import asyncio

@app.post("/summon")
async def summon_endpoint(request: Request, x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    data = await request.json()
    resp = handle_summon(data)
    return JSONResponse(content=resp)

@app.post("/api/summon/sync")
async def sync_endpoint(request: Request, x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    data = await request.json()
    from services.summon_service import handle_sync
    resp = handle_sync(data)
    return JSONResponse(content=resp)

@app.post("/api/summon/sync/batch")
async def sync_batch_endpoint(request: Request, x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    data = await request.json()
    from services.summon_service import handle_sync_batch
    resp = handle_sync_batch(data)
    return JSONResponse(content=resp)

@app.get("/players")
def players_endpoint(x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    return {"players": get_players_service()}

@app.post("/nfc-event")
async def nfc_event_endpoint(request: Request, x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    data = await request.json()
    return handle_nfc_event_service(data)