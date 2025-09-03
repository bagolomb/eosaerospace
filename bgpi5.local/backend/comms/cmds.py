from backend.drone import arm
from backend.drone import disarm
from backend.drone import takeoff
from backend.drone import land
from backend.drone import hold
from backend.drone import offboard_start
from backend.drone import offboard_stop

handlers = {}

def cmd(name: str):
    def wrap(fn):
        handlers[name] = fn
        return fn
    return wrap

@cmd("arm")
async def _():
    await arm()

@cmd("disarm")
async def _():
    await disarm()

@cmd("takeoff")
async def _():
    await takeoff()

@cmd("land")
async def _():
    await land()

@cmd("hold")
async def _():
    await hold()

@cmd("offboard_start")
async def _():
    await offboard_start()

@cmd("offboard_stop")
async def _():
    await offboard_stop()


