import asyncio
import time
from typing import Any, Dict, List
import sys
import websockets

from utils import encode, decode

if len(sys.argv) < 2:
    print(f"Syntax {sys.argv[0]} [room]")
    sys.exit(-1)

room: str = sys.argv[1]
trigger_count: float = 5000.0


async def reader(websocket):
    count: int = 0
    seq: int = 0
    last_time: int = time.monotonic()
    client_id: int = None
    last_msg_id: int = None

    async for message_raw in websocket:
        count += 1
        msg = decode(message_raw)

        if msg["type"] == "joined":
            client_id = msg["client_id"]
        else:
            msg_id = msg["msg_id"]
            if last_msg_id is None:
                last_msg_id == msg_id
            elif msg_id != (last_msg_id + 1):
                    print(last_msg_id, msg_id)
                    raise Exception("bad msg sequence")

        if msg["type"] == "ping" and client_id == msg["client_id"] and msg["seq"] != seq:
            print(seq, message_raw)
            raise Exception("bad message seq")

        if count >= trigger_count:
            next_time = time.monotonic()
            print(f"{count /(next_time - last_time)}/s {room}")
            last_time = time.monotonic()
            count = 0

        if client_id == msg["client_id"]:
            seq += 1
            await websocket.send(encode({"type": "ping", "seq": seq}))


async def connect():
    uri: str = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connecting")
            await websocket.send(encode({"type": "join", "room": room}))
            consumer_task = asyncio.ensure_future(reader(websocket))
            done = await asyncio.wait(
                [consumer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
    except IOError as error:
        print("Could not connect - is the server running? Do you have network access?")


asyncio.get_event_loop().run_until_complete(connect())
