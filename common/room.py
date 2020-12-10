from asyncio import Queue
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .client import Client


@dataclass
class Room:
    key: str
    clients: Dict[int, Client] = field(default_factory=dict)
    new_clients: List[Client] = field(default_factory=list)
    msg_id: int = 0
    event_queue: Queue = field(default_factory=Queue)
    listening: bool = False
    future: Any = None

    def client_count(self) -> int:
        return len([c.id for c in self.clients.values() if not c.disconnected])
