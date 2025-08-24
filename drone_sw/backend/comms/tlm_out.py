mport asyncio
import time
from .helpers import send_json

GS_HOST = "LAP-MBP-0583.local"
TLM_PORT = 9001

async def telemetry_sender():
    while True:
        try:
            _, writer = await asyncio.open_connection(GS_HOST, TLM_PORT)
            print("[Drone] Connected to GS telemetry server")

            while True:
                msg = {"ts": time.time()}
                await send_json(writer, msg)
                await asyncio.sleep(1)

        except Exception as e:
            print("[Drone] Telemetry error:", e)
            await asyncio.sleep(2)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass