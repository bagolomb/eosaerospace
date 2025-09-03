# start.py
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "frontend"

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
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "backend.app",
        cwd=str(ROOT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    print("[backend] started")

    async for line in proc.stdout:
        print("[backend]", line.decode().rstrip())

async def main():
    # run both processes concurrently
    await asyncio.gather(start_svelte(), start_backend())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
