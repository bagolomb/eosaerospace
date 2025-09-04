import asyncio, logging, sys
from backend.comms.server import starter as tcp_starter  # this is your TCP server (start_server)
from backend import drone

async def _connect_drone_forever():
    while True:
        try:
            await drone.connect()
            logging.info("[drone] connected")
            return
        except Exception as e:
            logging.error(f"[drone] connect failed: {e}; retrying in 2s")
            await asyncio.sleep(2)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Start TCP server immediately (serves forever)
    tcp_task = asyncio.create_task(tcp_starter(), name="tcp-serial")

    # Connect to the drone concurrently (don’t block server startup)
    drone_task = asyncio.create_task(_connect_drone_forever(), name="drone-connect")

    # Wait on both (tcp_task runs forever; ctrl+c stops)
    await asyncio.gather(tcp_task, drone_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
