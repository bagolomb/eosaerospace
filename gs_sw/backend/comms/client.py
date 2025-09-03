import asyncio
import signal
import websockets
import msgspec
import struct
import orjson
from pathlib import Path
from datetime import datetime
from serial_asyncio_fast import open_serial_connection

from backend import config

decoder = msgspec.msgpack.Decoder()

def unpack_tlm(tlm):
    return decoder.decode(tlm)

MSG_INFO = {
    0 : {
        "kind" : "CMD",
        "format" : "<BB"
    },
    1 : {
        "id" : "RC",
        "format" : "<B4h"
    },
}

CMD_MAPPING = {
    "arm" : 0,
    "disarm" : 1,
    "takeoff" : 2,
    "land" : 3,
    "hold" : 4,
    "offboard_start" : 5,
    "offboard_stop" : 6
}

def _ts(): 
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def _mklog(prefix: str) -> Path:
    p = Path("logs"); p.mkdir(parents=True, exist_ok=True)
    return p / f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

IN_LOG  = _mklog("incoming")
OUT_LOG = _mklog("outgoing")

def log_append(path: Path, data: bytes):
    # simple, single-process append; for higher throughput you could buffer
    with path.open("ab", buffering=0) as f:
        f.write(f"[{_ts()}] {len(data)} bytes\n".encode())
        f.write(data); f.write(b"\n")

# --- serial manager: auto reconnect, yields reader/writer ---
async def open_serial_loop(stop: asyncio.Event):
    backoff = 0.25
    while not stop.is_set():
        try:
            reader, writer = await open_serial_connection(
                url=config.PI5_SERIAL_ADDR,
                baudrate=115200
            )
            print("[serial] connected")
            return reader, writer
        except Exception as e:
            print(f"[serial] connect failed: {e}")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 2.0)
    raise asyncio.CancelledError  # stop triggered

async def ws_handler(ws):
    stop = asyncio.Event()
    reader, writer = await open_serial_loop(stop)

    async def serial_to_ws():
        try:
            while not stop.is_set():
                raw = await reader.readline()
                msg = raw.rstrip(b"\n") 
                tlm = unpack_tlm(msg)
                log_append(OUT_LOG, tlm)
                await ws.send(tlm)  # forward to frontend
        except Exception as e:
            print(f"[serial->ws] {e}")
            stop.set()

    async def ws_to_serial():
        try:
            async for msg in ws:
                data = orjson.loads(msg) 
                if "cmd" in data:
                    writer.write(struct.pack(MSG_INFO[0]["format"], 0, CMD_MAPPING[data["cmd"]]))
                elif "rc" in data:
                    writer.write(struct.pack(MSG_INFO[1]["format"], 1, *data["rc"]))
                log_append(IN_LOG, data)
                await writer.drain()
        except Exception as e:
            print(f"[ws->serial] {e}")
        finally:
            stop.set()

    tasks = [
        asyncio.create_task(serial_to_ws()),
        asyncio.create_task(ws_to_serial()),
    ]
    await stop.wait()
    for t in tasks: t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    try:
        writer.close()
        await writer.wait_closed()
    except: pass

async def starter(stop: asyncio.Event | None = None):
    stop = stop or asyncio.Event()
    loop = asyncio.get_running_loop()
    if stop is None:
        def _sig(*_): stop.set()
        for s in (signal.SIGINT, signal.SIGTERM):
            try: loop.add_signal_handler(s, _sig)
            except NotImplementedError: pass

    server = await websockets.serve(ws_handler, config.FRONTEND_HOST, config.FRONTEND_PORT, max_size=None)
    print(f"[ws] bridge running on {config.FRONTEND_PORT}")
    try:
        await stop.wait()
    finally:
        server.close(); await server.wait_closed()