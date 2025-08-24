import asyncio

# --- queues/state ---
event_queue = asyncio.Queue()
latest_control = None

# --- API for your core app logic ---
async def send_event(cmd: dict):
    """Enqueue a reliable FIFO command (arm, takeoff, mode change)."""
    await event_queue.put({"type": "event", **cmd})

def set_control(cmd: dict):
    """Update the latest control state (joystick, setpoints)."""
    global latest_control
    latest_control = {"type": "control", **cmd}

async def get_next_command():
    """Return the next command to send, preferring latest control."""
    global latest_control

    # Prioritize latest control
    if latest_control:
        cmd = latest_control
        latest_control = None
        return cmd

    # Otherwise get from FIFO event queue
    if not event_queue.empty():
        return await event_queue.get()

    return None
