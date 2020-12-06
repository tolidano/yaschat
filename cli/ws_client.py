from typing import *
import asyncio, json, websockets, time, sys

from utils import encode, decode

if len(sys.argv) < 2:
    print(f"Sytnax {sys.argv[0]} room (delay)")
    sys.exit(-1)

room = sys.argv[1]
slow = 0.0
if len(sys.argv) > 2:
    slow = float(sys.argv[2])

trigger_count = 5000.0
if slow > 0:
    trigger_count /= (1 + slow) * 100


async def reader(websocket):
    count = 0
    seq = 0
    last_time = time.monotonic()
    client_id = None
    last_msg_id = None

    async for message_raw in websocket:
        count += 1
        msg = decode(message_raw)

        if msg["type"] == "joined":
            client_id = msg["client_id"]
        else:
            msg_id = msg["msg_id"]
            if last_msg_id is None:
                last_msg_id == msg_id
            else:
                if msg_id != (last_msg_id + 1):
                    print(last_msg_id, msg_id)
                    raise Exception("bad msg sequence")

        if msg["type"] == "ping" and client_id == msg["client_id"]:
            if msg["seq"] != seq:
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

        if slow > 0:
            await asyncio.sleep(slow)


async def connect():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print("Connecting")
        await websocket.send(encode({"type": "join", "room": room}))
        consumer_task = asyncio.ensure_future(reader(websocket))
        done = await asyncio.wait(
            [consumer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )


asyncio.get_event_loop().run_until_complete(connect())
