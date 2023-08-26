import asyncio
import logging
from collections.abc import Awaitable, Mapping
from types import MappingProxyType
from typing import Any, Optional, TypeVar, Union

import uvicorn
from fastapi import FastAPI
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket

from components.api import API
from components.jsonpersistence import JSONPersistence
from components.objects import Poll, PollVote
from components.websocketmanager import WebSocketManager

_logger = logging.getLogger(__name__)

_RT = TypeVar("_RT")


class Controller:
    def __init__(self, persistence: JSONPersistence, debug_mode: bool = False) -> None:
        self.fast_api: FastAPI = FastAPI(
            routes=[
                Mount("/static", StaticFiles(directory="static"), name="static"),
            ],
            redoc_url=None,
            docs_url="/docs" if debug_mode else None,
        )
        self.api = API(self)
        self.websocket_manager = WebSocketManager()
        self.persistence: JSONPersistence = persistence

        self._polls: dict[str, Poll] = {}
        self.polls: Mapping[str, Poll] = MappingProxyType(self._polls)
        self._active_poll: Optional[Poll] = None

        self._running = False
        self._spawned_tasks: set[asyncio.Task] = set()

    @property
    def running(self) -> bool:
        return self._running

    @property
    def active_poll(self) -> Optional[Poll]:
        return self._active_poll

    @property
    def idle(self) -> bool:
        return self._active_poll is None

    async def update_active_poll(
        self, poll: Union[Poll, str], exclude_websocket: Optional[WebSocket] = None
    ) -> None:
        if isinstance(poll, str):
            if (effective_poll := self.polls.get(poll)) is None:
                raise ValueError(f"Unknown poll id {effective_poll}")
        elif not isinstance(poll, Poll):
            raise TypeError(f"Expected Poll or str, got {type(poll)}")
        else:
            effective_poll = poll

        self._active_poll = effective_poll

        if effective_poll.uid not in self.polls:
            self._polls[effective_poll.uid] = effective_poll
            self.create_task(self.persistence.update_poll(effective_poll))

        self.create_task(
            self.websocket_manager.broadcast_active_poll(effective_poll, exclude=exclude_websocket)
        )

    async def stop_active_poll(self, exclude_websocket: Optional[WebSocket] = None) -> None:
        self._active_poll = None
        self.create_task(self.websocket_manager.broadcast_idle(exclude_websocket))

    async def add_poll_vote(self, poll_vote: PollVote) -> None:
        if (poll := self.polls.get(poll_vote.poll_uid)) is None:
            raise ValueError(f"Unknown poll id {poll_vote.poll_uid}")

        poll.add_vote(poll_vote)
        _logger.info("Added vote for poll %s: %s.", poll.uid, poll_vote)
        self.create_task(self.persistence.update_poll(poll))

    async def start(self) -> None:
        await self.persistence.initialize()
        self._polls.update(await self.persistence.get_polls())
        self._running = True

    async def stop(self) -> None:
        await asyncio.gather(*self._spawned_tasks, return_exceptions=True)
        await self.persistence.update_polls(self._polls)
        await self.persistence.shutdown()
        self._running = False

    async def run(
        self,
        port: int = 8000,
        log_level: int = logging.WARNING,
        use_colors: bool = False,
        **kwargs: Any,
    ) -> None:
        await self.start()
        server = uvicorn.Server(
            config=uvicorn.Config(
                app=self.fast_api, port=port, log_level=log_level, use_colors=use_colors, **kwargs
            )
        )
        await server.serve()
        await self.stop()

    def create_task(
        self,
        coroutine: Awaitable[_RT],
        name: Optional[str] = None,
    ) -> "asyncio.Task[_RT]":
        task = asyncio.create_task(
            self.__create_task_callback(coroutine), name=name or repr(coroutine)
        )

        if self.running:
            self._spawned_tasks.add(task)
            task.add_done_callback(self._spawned_tasks.discard)
        else:
            _logger.warning(
                "Tasks created via `Controller.create_task` while the controller is not "
                "running won't be automatically awaited!"
            )

        return task

    @staticmethod
    async def __create_task_callback(
        coroutine: Awaitable[_RT],
    ) -> Any:
        try:
            return await coroutine
        except Exception as exception:  # pylint: disable=broad-except
            _logger.exception("Coroutine %s raised exception.", coroutine, exc_info=exception)
