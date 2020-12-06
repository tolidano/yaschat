from dataclasses import dataclass
from typing import Any


@dataclass
class Client:
    socket: Any
    id: int
    disconnected: bool = False
