import orjson

async def send_json(writer, json):
    writer.write(orjson.dumps(json) + b"\n")
    await writer.drain()

async def read_json(reader):
    line = await reader.readline()
    if not line:
        return None
    return orjson.loads(line)
    
    