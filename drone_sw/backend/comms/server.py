# DRONE SIDE (host TCP that behaves like serial)
import asyncio, signal, contextlib, msgspec, struct
from backend.comms.cmds import handlers
from backend import config, drone

MSG_INFO = {
    0: {"kind": "CMD", "format": "<BB"},
    1: {"kind": "RC",  "format": "<B4h"},  # use "<B4hH" only if you truly have flags and unpack 6
}
encoder = msgspec.msgpack.Encoder()
def pack_tlm(tlm): return encoder.encode(tlm)

async def tlm_loop(writer):
    wait_time = 1.0 / config.TLM_HZ
    while True:
        tlm = await drone.get_tlm()
        writer.write(pack_tlm(tlm) + b"\n")
        await writer.drain()
        await asyncio.sleep(wait_time)

async def cmd_loop(reader):
    while True:
        raw = await reader.readline()
        if not raw:
            raise asyncio.IncompleteReadError(partial=b"", expected=1)
        msg = raw.rstrip(b"\n")
        if not msg:
            continue
        k = msg[0]
        if k == 0:
            _, cmd = struct.unpack(MSG_INFO[k]["format"], msg)
            print(f"running cmd: {cmd}")
            fn = handlers.get(cmd)
            if fn: await fn()
            else:  print(f"Unknown cmd id: {cmd}")
        elif k == 1:
            _, x, y, z, r = struct.unpack(MSG_INFO[k]["format"], msg)
            to_unit = lambda v: max(-1.0, min(1.0, v / 32767))
            await drone.rc(to_unit(x), to_unit(y), to_unit(z), to_unit(r))
        else:
            print("Unknown msg kind:", k)

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    print(f"[tcp] GS connected: {peer}")
    tx = asyncio.create_task(tlm_loop(writer))
    rx = asyncio.create_task(cmd_loop(reader))
    try:
        await asyncio.wait({tx, rx}, return_when=asyncio.FIRST_EXCEPTION)
    finally:
        for t in (tx, rx):
            t.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await tx; await rx
        writer.close()
        with contextlib.suppress(Exception):
            await writer.wait_closed()
        print(f"[tcp] GS disconnected: {peer}")

async def run_server(host="0.0.0.0", port=5555):
    srv = await asyncio.start_server(handle_client, host, port)
    addrs = ", ".join(str(s.getsockname()) for s in srv.sockets or [])
    print(f"[tcp] listening on {addrs}")
    async with srv:
        await srv.serve_forever()

async def starter():
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(s, stop.set)
    task = asyncio.create_task(run_server(host="0.0.0.0", port=5555))
    await stop.wait()
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task
