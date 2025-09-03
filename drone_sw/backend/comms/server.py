import asyncio
import signal
import contextlib
from serial_asyncio_fast import open_serial_connection
import msgspec
import struct

from backend.comms.cmds import handlers
from backend import config
from backend import drone

MSG_INFO = {
    0 : {
        "kind" : "CMD",
        "format" : "<BB"
    },
    1 : {
        "kind" : "RC",
        "format" : "<B4hH"
    }
}

encoder = msgspec.msgpack.Encoder()

def pack_tlm(tlm):
    return encoder.encode(tlm)

async def run_serial():
    while True:
        try:
            reader, writer = await open_serial_connection(
                url=config.GS_SERIAL_ADDR,
                baudrate=115200
            )
            print("Serial connected")
            # run loops until failure
            await asyncio.gather(
                tlm_loop(writer),
                cmd_loop(reader),
            )
        except Exception as e:
            print("Serial error:", e)
        finally:
            print("Reconnecting in 2s…")
            await asyncio.sleep(2)

async def tlm_loop(writer):
    wait_time = 1.0/config.TLM_HZ
    while True:
        tlm = await drone.get_tlm()
        writer.write(pack_tlm(tlm) + b"\n")
        await writer.drain()
        await asyncio.sleep(wait_time)

async def cmd_loop(reader):
    while True:
        raw = await reader.readline()
        msg = raw.rstrip(b"\n")
        msg_kind = msg[0]
        if msg_kind == 0:
            _, cmd = struct.unpack(MSG_INFO[msg_kind]["format"], msg)
            print("running cmd:" + cmd)
            await handlers[cmd]()
        elif msg_kind == 1:
            _, x,y,z,r = struct.unpack(MSG_INFO[msg_kind]["format"],msg)
            x = x/32767
            y = y/32767
            z = z/32767
            r = r/32767
            await drone.rc(x,y,z,r)
        else:
            print("Unknown msg kind:", msg_kind)

async def starter():
    """App entry: run serial + handle SIGINT/SIGTERM cleanly."""
    stop = asyncio.Event()

    def _sig(*_):
        stop.set()

    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(s, _sig)
        except NotImplementedError:
            pass

    serial_task = asyncio.create_task(run_serial())
    await stop.wait()
    serial_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await serial_task