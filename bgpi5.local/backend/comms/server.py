import asyncio
import signal
import websockets
import msgspec

from backend.comms.cmds import handlers
from backend import config
from backend import drone

CMD = 0
RC = 1

encoder = msgspec.msgpack.Encoder()
decoder = msgspec.msgpack.Decoder()

def pack_tlm(tlm):
    return encoder.encode(tlm)

def unpack_msg(data):
    return decoder.decode(data)

async def tlm_handler(ws, _):
    wait_time = 1.0/config.TLM_HZ
    try:
        while True:
            tlm = await drone.get_tlm()
            await ws.send(pack_tlm(tlm))
            await asyncio.sleep(wait_time)
    except websockets.ConnectionClosed:
        pass

async def cmd_handler(ws, _):
    try:
        while True:
            msg = await ws.recv()
            msg_arr = unpack_msg(msg)
            msg_kind = msg_arr[0]
            msg_payload = msg_arr[1]

            if msg_kind == CMD:
                cmd_name = msg_payload
                await handlers[cmd_name]()
            elif msg_kind == RC:
                await handlers["rc"](msg_payload)
            else:
                print(f"Unkown msg kind: {msg_kind}")

    except websockets.ConnectionClosed:
        pass


async def starter():
    stop = asyncio.Event()
    def _sig(*_):
        stop.set()
    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        try: 
            loop.add_signal_handler(s, _sig)
        except NotImplementedError: 
            pass

    async with websockets.serve(tlm_handler, config.DRONE_TLM_HOST, config.DRONE_TLM_PORT),\
        websockets.serve(cmd_handler, config.DRONE_CMD_HOST, config.DRONE_CMD_PORT):
        await stop.wait()
