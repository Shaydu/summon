

# --- Modular FastAPI app (v3.4) ---
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from services.summon_service import handle_summon
from services.player_service import get_players as get_players_service
from services.nfc_service import handle_nfc_event as handle_nfc_event_service
from services.chat_service import handle_chat
from services.give_service import handle_give
from services.say_service import handle_say
from services.time_service import handle_time
from services.device_location_service import handle_device_location


app = FastAPI(title="NFC → Minecraft API v3.6")
# Serve resized mob images and web UI
app.mount("/mob_images", StaticFiles(directory="web/mob_images"), name="mob_images")
app.mount("/web", StaticFiles(directory="web"), name="web")
@app.post("/give")
async def give_endpoint(request: Request, x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    data = await request.json()
    resp = handle_give(data)
    return JSONResponse(content=resp)

@app.post("/chat")
async def chat_endpoint(request: Request, x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    data = await request.json()
    resp = handle_chat(data)
    return JSONResponse(content=resp)


@app.post("/say")
async def say_endpoint(request: Request, x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    data = await request.json()
    resp = handle_say(data)
    if isinstance(resp, dict) and resp.get("status") == "error":
        return JSONResponse(content=resp, status_code=400)
    return JSONResponse(content=resp)


@app.post("/time")
async def time_endpoint(request: Request, x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    data = await request.json()
    resp = handle_time(data)
    if isinstance(resp, dict) and resp.get("status") == "error":
        return JSONResponse(content=resp, status_code=400)
    return JSONResponse(content=resp)

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


@app.post("/api/device/location")
async def device_location_endpoint(request: Request, x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    data = await request.json()
    resp = handle_device_location(data)
    if isinstance(resp, dict) and resp.get("status") == "error":
        return JSONResponse(content=resp, status_code=400)
    return JSONResponse(content=resp)


@app.get("/summons")
def summons_list_endpoint(x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    from summon_db import get_all_summons

    summons = get_all_summons()
    return {"status": "ok", "summons": summons}


@app.get("/mobs")
def mobs_list(x_api_key: str = Header(...)):
    """Return list of mobs available in web/mob_images directory.
    Requires `x-api-key` header."""
    require_api_key(x_api_key)
    imgs_dir = os.path.join("web", "mob_images")
    mobs = []
    try:
        for f in sorted(os.listdir(imgs_dir)):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                name = os.path.splitext(f)[0]
                mobs.append({"name": name, "image": f"/mob_images/{f}"})
    except FileNotFoundError:
        mobs = []
    return {"mobs": mobs}


@app.get("/mobs/{mob}")
def mob_detail(mob: str, x_api_key: str = Header(...)):
    """Return mob detail: image URL and list of summons for that mob."""
    require_api_key(x_api_key)
    # find image
    imgs_dir = os.path.join("web", "mob_images")
    candidates = []
    try:
        for f in sorted(os.listdir(imgs_dir)):
            if os.path.splitext(f)[0].lower() == mob.lower():
                candidates.append(f)
    except FileNotFoundError:
        candidates = []
    # fallback to mob/ originals
    if not candidates:
        try:
            for f in sorted(os.listdir("mob")):
                if os.path.splitext(f)[0].lower() == mob.lower():
                    candidates.append(f)
        except FileNotFoundError:
            candidates = []
    if not candidates:
        raise HTTPException(status_code=404, detail="Mob not found")
    image_file = candidates[0]
    image_url = f"/mob_images/{image_file}" if os.path.exists(os.path.join("web","mob_images", image_file)) else f"/mob/{image_file}"

    from summon_db import get_summons_by_mob
    summons = get_summons_by_mob(mob)
    # build map link if gps present
    for s in summons:
        lat = s.get("gps_lat")
        lon = s.get("gps_lon")
        if lat is not None and lon is not None:
            s["map_url"] = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}"
        else:
            s["map_url"] = None

    return {"name": mob, "image": image_url, "summons": summons}

@app.get("/players")
def players_endpoint(x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    return {"players": get_players_service()}

@app.post("/nfc-event")
async def nfc_event_endpoint(request: Request, x_api_key: str = Header(...)):
    require_api_key(x_api_key)
    data = await request.json()
    return handle_nfc_event_service(data)