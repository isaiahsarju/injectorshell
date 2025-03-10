#Thanks https://websockets.readthedocs.io/en/3.0/intro.html
import asyncio
import websockets

async def capture(websocket, path):
    msg = await websocket.recv()
    print(f"{msg}")

start_server = websockets.serve(capture, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
try:
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    exit()