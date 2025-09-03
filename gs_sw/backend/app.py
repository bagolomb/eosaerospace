# backend/app.py
import asyncio
import signal
from backend.comms.client import starter as ws_starter

async def main():
    try:
        print("Controller initialized")
    except RuntimeError as e:
        print(f"No controller: {e}")
        
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        try: 
            loop.add_signal_handler(s, stop.set)
        except NotImplementedError:
            pass

    tasks = [
        asyncio.create_task(ws_starter(stop),       name="ws"),   # pass shared stop
    ]
    await stop.wait()
    for t in tasks: 
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass