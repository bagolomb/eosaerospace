import asyncio
import comms.starter
import drone

def main():
    asyncio.run(drone.connect())
    asyncio.run(comms.starter())


