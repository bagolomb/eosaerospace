import asyncio
import signal
import websockets
import msgspec
import struct
import orjson
from pathlib import Path
from datetime import datetime
from typing import Optional
import socket

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
    # Place logs under gs_sw/logs regardless of CWD
    base = Path(__file__).resolve().parents[2] / "logs"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

IN_LOG  = _mklog("incoming")
OUT_LOG = _mklog("outgoing")

def log_append(path: Path, data):
    # Accept bytes/str/JSON-serializable objects; append as bytes per line
    if isinstance(data, (bytes, bytearray)):
        payload = bytes(data)
    elif isinstance(data, str):
        payload = data.encode()
    else:
        # Fallback to JSON for objects
        payload = orjson.dumps(data)
    with path.open("ab", buffering=0) as f:
        f.write(f"[{_ts()}] {len(payload)} bytes\n".encode())
        f.write(payload)
        f.write(b"\n")

# --- serial manager: auto reconnect, yields reader/writer ---
async def open_serial_loop(stop: asyncio.Event):
    backoff = 0.25
    host, port = "192.168.0.155", 5555   # hardcode just to isolate parsing issues
    loop = asyncio.get_running_loop()

    while not stop.is_set():
        try:
            # Resolve explicitly to IPv4 to avoid any v6/happy-eyeballs weirdness
            infos = await loop.getaddrinfo(
                host, port, family=socket.AF_INET, type=socket.SOCK_STREAM
            )
            if not infos:
                raise OSError("getaddrinfo returned no results")

            last_err = None
            for fam, typ, proto, _, addr in infos:
                try:
                    print(f"[serial] trying {addr} (AF_INET)", flush=True)
                    reader, writer = await asyncio.open_connection(
                        addr[0], addr[1],
                        family=fam, proto=proto, ssl=None,
                        # optional but can help on macOS stacks:
                        happy_eyeballs_delay=None,
                    )
                    print("[serial] connected", flush=True)
                    return reader, writer
                except Exception as e:
                    last_err = e
                    print(f"[serial] attempt {addr} failed: {type(e).__name__}: {e}", flush=True)
            raise last_err
        except Exception as e:
            print(f"[serial] connect failed: {type(e).__name__}: {e!s}", flush=True)
            await asyncio.sleep(backoff); backoff = min(backoff*2, 2.0)
    raise asyncio.CancelledError

async def ws_handler(ws):
    stop = asyncio.Event()
    reader, writer = await open_serial_loop(stop)
    try:
        peer = getattr(ws, "remote_address", None)
        print(f"[ws] frontend connected: {peer}")
    except Exception:
        print("[ws] frontend connected")

    async def serial_to_ws():
        try:
            first = True
            while not stop.is_set():
                raw = await reader.readline()
                msg = raw.rstrip(b"\n") 
                tlm = unpack_tlm(msg)
                # Forward as JSON text to frontend and log bytes
                payload = orjson.dumps(tlm)
                log_append(OUT_LOG, payload)
                await ws.send(payload.decode())
                if first:
                    print("[serial->ws] telemetry forwarding active")
                    first = False
        except Exception as e:
            print(f"[serial->ws] {e}")
            stop.set()

    async def ws_to_serial():
        try:
            async for msg in ws:
                data = orjson.loads(msg) 
                if "cmd" in data:
                    cmd_name = data["cmd"]
                    cmd_id = CMD_MAPPING.get(cmd_name)
                    if cmd_id is None:
                        print(f"[ws->serial] unknown cmd '{cmd_name}'")
                        continue
                    writer.write(struct.pack(MSG_INFO[0]["format"], 0, cmd_id)+b"\n")
                    print(f"[ws->serial] sent CMD '{cmd_name}' ({cmd_id})")
                elif "rc" in data:
                    writer.write(struct.pack(MSG_INFO[1]["format"], 1, *data["rc"])+b"\n")
                # Log the incoming WS JSON payload
                log_append(IN_LOG, msg)
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
    try:
        peer = getattr(ws, "remote_address", None)
        print(f"[ws] frontend disconnected: {peer}")
    except Exception:
        print("[ws] frontend disconnected")

async def starter(stop: Optional[asyncio.Event] = None):
    new_stop_created = False
    if stop is None:
        stop = asyncio.Event()
        new_stop_created = True

    loop = asyncio.get_running_loop()

    # only install signal handlers when we created the stop (i.e., top-level run)
    if new_stop_created:
        def _sig(*_): stop.set()
        for s in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(s, _sig)
            except NotImplementedError:
                pass

    server = await websockets.serve(
        ws_handler,
        config.FRONTEND_HOST,
        config.FRONTEND_PORT,
        max_size=None
    )
    print(f"[ws] bridge running on {config.FRONTEND_PORT}")

    try:
        await stop.wait()
    finally:
        server.close()
        await server.wait_closed()
