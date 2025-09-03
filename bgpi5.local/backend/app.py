import asyncio
from backend.comms.server import starter as comms_starter
from backend import drone

async def main():
    # Step 1: Connect to drone
    await drone.connect()

    # Step 2: Start websocket server (blocks forever until stopped)
    await comms_starter()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
