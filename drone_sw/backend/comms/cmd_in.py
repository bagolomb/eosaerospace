import asyncio
from .helpers import read_json

GS_HOST = "LAP-MBP-0583.local"
CMD_PORT = 9000

async def command_receiver():
    while True:
        try:
            reader, writer = await asyncio.open_connection(GS_HOST, CMD_PORT)
            print("[Drone] Connected to GS command server")

            while True:
                msg = await read_json(reader)
                if msg is None:
                    print("[Drone] Command stream closed")
                    break

                if msg["type"] == "event":
                    print("[Drone] Event command:", msg)
                    # integrate into autopilot (arm/takeoff/etc.)
                elif msg["type"] == "control":
                    print("[Drone] Control command:", msg)
                    # update setpoints (roll, pitch, yaw, throttle)

        except Exception as e:
            print("[Drone] Command error:", e)
            await asyncio.sleep(2)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
