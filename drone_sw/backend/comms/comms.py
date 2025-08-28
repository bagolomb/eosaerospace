import asyncio
import signal
import websockets
import msgspec
from cmds import handlers
import config
import drone

CMD = 0
RC = 1

encoder = msgspec.msgpack.Encoder()
decoder = msgspec.msgpack.Decoder()

def pack_cmd(kind, payload):
    return encoder.encode([kind, payload])

def pack_tlm(tlm):
    return encoder.encode(tlm)

def unpack(data):
    return decoder.decode(data)

async def connect(addr):
    backoff = 1
    while True:
        try:
            ws = await websockets.connect(addr)
            return ws
        except Exception as e:
            print(f"Connection error: {e}")
            await asyncio.sleep(backoff)

async def tlm_ws():
    while True:
        ws = await connect(config.GS_TLM_ADDR)
        try:
            while True:
                tlm = await drone.get_tlm()
                await ws.send(pack_tlm(tlm))
        except Exception as e:
            print(f"Error: {e}")
            try: 
                await ws.close()
            except: 
                pass

async def cmd_ws():
    while True:
        ws = await connect(config.GS_CMD_ADDR)
        try:
            while True:
                data = await ws.recv()
                kind, payload = unpack(data)
                if kind == CMD:
                    handlers[payload["cmd"]](payload)
                elif kind == RC:
                    pass
        except Exception as e:
            print(f"Error: {e}")
            try: 
                await ws.close()
            except: 
                pass


async def starter():
    stop = asyncio.Event()
    def _sig(*_):
        stop.set()
    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            asyncio.get_running_loop().add_signal_handler(s, _sig)
        except NotImplementedError:
            pass
    tasks = [asyncio.create_task(tlm_ws()), asyncio.create_task(cmd_ws())]
    await stop.wait()
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


def main():
    asyncio.run(starter())