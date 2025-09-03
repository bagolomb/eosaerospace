from mavsdk import System
from mavsdk.offboard import VelocityNedYaw
import asyncio
import time

from backend import config

drone = System()

async def connect():
    await drone.connect(system_address=config.DRONE_SERIAL_ADDR)
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break

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

async def disarm():
    await drone.action.disarm()

async def takeoff():
    await drone.action.takeoff()

async def land():
    await drone.action.land()

async def hold():
    await drone.action.hold()

async def offboard_start():
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    await drone.offboard.start()

async def offboard_stop():
    await drone.offboard.stop()

async def rc():
    pass