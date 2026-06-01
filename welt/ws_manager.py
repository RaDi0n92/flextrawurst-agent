# ws_manager.py — WebSocket Connection Manager für Gruppen-Chat
from fastapi import WebSocket
from typing import Dict, Set


class GroupChatManager:
    def __init__(self):
        self.rooms: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, group_id: int):
        await websocket.accept()
        if group_id not in self.rooms:
            self.rooms[group_id] = set()
        self.rooms[group_id].add(websocket)

    def disconnect(self, websocket: WebSocket, group_id: int):
        if group_id in self.rooms:
            self.rooms[group_id].discard(websocket)
            if not self.rooms[group_id]:
                del self.rooms[group_id]

    async def broadcast(self, group_id: int, message: dict, exclude: WebSocket = None):
        if group_id not in self.rooms:
            return
        dead = set()
        for ws in self.rooms[group_id]:
            if ws is exclude:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.rooms[group_id].discard(ws)

    def online_count(self, group_id: int) -> int:
        return len(self.rooms.get(group_id, set()))


manager = GroupChatManager()
