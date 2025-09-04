# start.py
import asyncio
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "frontend"

COMMON_ENV = {**os.environ, "FORCE_COLOR": "1"}

async def start_svelte():
    proc = await asyncio.create_subprocess_exec(
        "npm", "run", "dev", "--", "--host",
        cwd=str(FRONTEND_DIR),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    print("[svelte] started")

    async for line in proc.stdout:
        print("[svelte]", line.decode().rstrip())

async def start_backend():
    env = {**COMMON_ENV, "PYTHONUNBUFFERED": "1"}
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-u", "-m", "backend.app",   # <- -u here
        cwd=str(ROOT),
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    print("[backend] started", flush=True)
    while True:
        line = await proc.stdout.readline()
        if not line: break
        print("[backend]", line.decode(errors="replace").rstrip(), flush=True)


async def main():
    # run both processes concurrently
    await asyncio.gather(start_svelte(), start_backend())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
