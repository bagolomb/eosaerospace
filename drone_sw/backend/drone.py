from mavsdk import System
import config
import time

drone = System()

async def connect():
    await drone.connect(system_address=config.DRONE_SERIAL_ADDR)

async def _one(gen, timeout=0.25):
    # take exactly one value from an async generator, or None on timeout
    try:
        return await asyncio.wait_for(gen.__anext__(), timeout)
    except Exception:
        return None

async def get_tlm():
    tlm_json = {}
    tlm_json["ts"] = time.time()

    pos  = await _one(drone.telemetry.position())
    bat  = await _one(drone.telemetry.battery())

    if pos:
        tlm_json["lat"] = pos.latitude_deg
        tlm_json["lon"] = pos.longitude_deg
        tlm_json["alt"] = pos.relative_altitude_m
    if bat:
        tlm_json["bat"] = bat.remaining_percent
    
    return tlm_json

async def arm():
    await drone.action.arm()
            
