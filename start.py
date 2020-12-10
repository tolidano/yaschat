import asyncio
import websockets

from .server import Server


def main() -> None:
    print("Starting server")
    server = Server()
    start_server = websockets.serve(
        server.listen_socket, "localhost", 8765, ping_interval=5, ping_timeout=5
    )
    print("Server started")
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


main()
