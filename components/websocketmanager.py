import asyncio
from typing import Any, Optional

from starlette.websockets import WebSocket

from components.objects import Poll


class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()
        self.__lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)

    async def broadcast_active_poll(self, poll: Poll, exclude: Optional[WebSocket] = None) -> None:
        return await self.broadcast_json({"active_poll": poll.model_dump()}, exclude=exclude)

    async def broadcast_idle(self, exclude: Optional[WebSocket] = None) -> None:
        return await self.broadcast_json({"idle": True}, exclude=exclude)

    async def broadcast_poll_update(self, poll: Poll, exclude: Optional[WebSocket] = None) -> None:
        return await self.broadcast_json({"poll_update": poll.model_dump()}, exclude=exclude)

    async def broadcast_json(self, json: Any, exclude: Optional[WebSocket] = None) -> None:
        async with self.__lock:
            await asyncio.gather(
                *(
                    self.send_json(json, connection)
                    for connection in self.active_connections
                    if connection is not exclude
                )
            )

    async def send_json(self, json: Any, websocket: WebSocket) -> None:
        try:
            await websocket.send_json(json)
        except RuntimeError as exc:
            if ".send' after sending 'websocket.close'" in str(exc):
                self.active_connections.discard(websocket)
                return
