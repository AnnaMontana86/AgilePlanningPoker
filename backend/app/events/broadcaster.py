import asyncio
import json
from collections import defaultdict


class Broadcaster:
    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue]] = defaultdict(list)

    def subscribe(self, room_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._queues[room_id].append(q)
        return q

    def unsubscribe(self, room_id: str, q: asyncio.Queue) -> None:
        try:
            self._queues[room_id].remove(q)
        except ValueError:
            pass

    async def broadcast(self, room_id: str, event_type: str, data: dict) -> None:
        payload = json.dumps({"type": event_type, "data": data})
        dead: list[asyncio.Queue] = []
        for q in self._queues.get(room_id, []):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self.unsubscribe(room_id, q)


broadcaster = Broadcaster()
