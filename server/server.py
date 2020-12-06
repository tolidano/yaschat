import asyncio
from typing import Any, Dict, List
import websockets

from client import Client
from room import Room
from stats import Stats
from utils import encode, decode


class Server(object):
    client_id_count: int = 0
    rooms: Dict[str, Room] = {}

    @staticmethod
    async def listen_room(room):
        if room.listening:
            raise Exception(f"Already listening to {room.key}")

        room.listening = True
        print(f"Listen Room {room.key}")
        stats = Stats(f"Outgoing {room.key}")
        while True:
            qevent = await room.event_queue.get()
            if qevent == None:
                break

            if len(room.new_clients) > 0:
                for client in room.new_clients:
                    room.clients[client.id] = client
                room.new_clients = []

            room.msg_id += 1
            qevent["msg_id"] = room.msg_id

            count = 0
            disconnected: List[int] = []
            for client in room.clients.values():
                if client.disconnected:
                    disconnected.append(client.id)
                    continue
                count += 1

                try:
                    await client.socket.send(encode(qevent))
                except websockets.ConnectionClosed:
                    print("Lost client in send")
                    client.disconnected = True

            stats.incr(count)

            for d in disconnected:
                if room.clients[d]:
                    del room.clients[d]

        print(f"Unlisten Room {room.key}")
        room.listening = False


    async def listen_socket(self, websocket, path):
        print("connect", path)
        self.client_id_count += 1
        room: Optional[Room] = None
        client = Client(id=self.client_id_count, socket=websocket)

        stats = Stats("Incoming")
        try:
            async for message_raw in websocket:
                message = decode(message_raw)
                if message["type"] == "join":
                    # Get/create room
                    room_key = message["room"]
                    if not room_key in self.rooms:
                        room = Room(key=room_key)
                        self.rooms[room_key] = room

                        room.future = asyncio.ensure_future(Server.listen_room(room))
                    else:
                        room = self.rooms[room_key]

                    room.new_clients.append(client)

                    await websocket.send(encode({"type": "joined", "client_id": client.id}))

                elif room:
                    message["client_id"] = client.id
                    await room.event_queue.put(message)
                else:
                    await websocket.send(encode(message))
                stats.incr()
        except websockets.ConnectionClosed:
            pass
        except Exception as e:
            print(e)
            pass

        client.disconnected = True
        if room is not None:
            if room.client_count() == 0:
                await room.event_queue.put(None)
                del self.rooms[room.key]
                await room.future
                print(f"Cleaned Room {room.key}")

        print("disconnect", self.rooms)
