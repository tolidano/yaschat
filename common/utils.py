import json
from typing import Any, Dict


def encode(msg: Dict) -> str:
    return json.dumps(msg, ensure_ascii=False)


def decode(text: str) -> Dict[str, Any]:
    return json.loads(text)
