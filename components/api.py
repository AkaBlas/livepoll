import asyncio
import json
import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Annotated, Literal, Optional, Union

from fastapi import Cookie, HTTPException
from pydantic_core import ValidationError
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket, WebSocketDisconnect

from components.objects import Poll, PollCookie, PollVote
from components.websocketmanager import WebSocketManager

if TYPE_CHECKING:
    from components.controller import Controller

_logger = logging.getLogger(__name__)


class API:
    def __init__(self, controller: "Controller") -> None:
        self._controller: Controller = controller
        self._controller.fast_api.get("/api/activePoll", response_model=Poll)(self.get_active_poll)
        self._controller.fast_api.put("/api/makeIdle", response_model=Literal[True])(
            self.make_idle
        )
        self._controller.fast_api.put("/api/updatePoll", response_model=Literal[True])(
            self.update_poll
        )
        self._controller.fast_api.put("/api/refreshActivePollPage")(self.refresh_active_poll_page)

        self._controller.fast_api.websocket("/websocketVoting")(self.web_socket_voting)
        self._controller.fast_api.websocket("/websocketResults")(self.web_socket_results)
        self._controller.fast_api.websocket("/websocketAdmin")(self.web_socket_admin)

        self._controller.fast_api.get("/")(self.index_page)
        self._controller.fast_api.get("/activepoll")(self.active_poll_page)
        self._controller.fast_api.get("/admin")(self.admin_page)

    async def index_page(
        self, request: Request, poll_votes: Annotated[Optional[str], Cookie()] = None
    ) -> Response:
        poll_votes_object = PollCookie(poll_votes=json.loads(poll_votes) if poll_votes else {})

        if (active_poll := self._controller.active_poll) is None:
            current_option_uid = None
        elif poll_vote := poll_votes_object.poll_votes.get(active_poll.uid):
            current_option_uid = poll_vote.option_uid
        else:
            current_option_uid = None

        return Jinja2Templates(directory="static").TemplateResponse(
            "index.html.jinja2",
            context={
                "request": request,
                "active_poll": active_poll,
                "current_option_uid": current_option_uid,
            },
        )

    def _refresh_active_poll_with_delay(self, delay: float = 1.5) -> None:
        async def callback() -> None:
            await asyncio.sleep(delay)
            await self.refresh_active_poll_page()

        self._controller.create_task(callback())

    async def active_poll_page(self, request: Request) -> Response:
        out = Jinja2Templates(directory="static").TemplateResponse(
            "activepoll.html.jinja2",
            context={
                "request": request,
                "active_poll": self._controller.active_poll,
            },
        )
        self._refresh_active_poll_with_delay()
        return out

    async def admin_page(self, request: Request) -> Response:
        return Jinja2Templates(directory="static").TemplateResponse(
            "admin.html.jinja2",
            context={
                "request": request,
                "active_poll": self._controller.active_poll,
                "polls": self._controller.polls.values(),
            },
        )

    async def get_active_poll(self) -> Poll:
        if self._controller.active_poll is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No active poll")
        return self._controller.active_poll

    async def make_idle(self) -> Literal[True]:
        await self._controller.stop_active_poll()
        self._controller.create_task(self.refresh_admin_page())
        return True

    async def update_poll(self, poll: Union[Poll, str]) -> Literal[True]:
        await self._controller.update_active_poll(poll)
        self._controller.create_task(self.refresh_admin_page())
        return True

    async def refresh_active_poll_page(self) -> None:
        if self._controller.active_poll is None:
            await self._controller.ws_manager_results.broadcast_idle()
            return
        await self._controller.ws_manager_results.broadcast_active_poll(
            self._controller.active_poll
        )

    async def refresh_admin_page(self) -> None:
        if self._controller.active_poll is None:
            await self._controller.ws_manager_admin.broadcast_idle()
            return
        await self._controller.ws_manager_admin.broadcast_active_poll(self._controller.active_poll)

    async def _handle_websocket_disconnect(
        self, ws_manager: WebSocketManager, websocket: WebSocket
    ) -> None:
        await ws_manager.disconnect(websocket)

    async def _handle_websocket_add_poll_vote(self, poll_vote: PollVote) -> None:
        await self._controller.add_poll_vote(poll_vote)
        await self._controller.ws_manager_admin.broadcast_poll_update(
            self._controller.polls[poll_vote.poll_uid]
        )

    async def web_socket_voting(self, websocket: WebSocket) -> None:
        await self._controller.ws_manager_voting.connect(websocket)
        try:
            while True:
                json_data = await websocket.receive_json()
                if poll_vote_data := json_data.get("add_poll_vote"):
                    try:
                        poll_vote = PollVote(**poll_vote_data)
                    except ValidationError as exc:
                        _logger.exception(
                            "Websocket got invalid data `%s` for `add_poll_vote`. Ignoring.",
                            poll_vote_data,
                            exc_info=exc,
                        )
                        continue

                    await self._handle_websocket_add_poll_vote(poll_vote)
                else:
                    _logger.warning("Websocket got unknown data `%s`. Ignoring.", json_data)
        except WebSocketDisconnect:
            await self._handle_websocket_disconnect(self._controller.ws_manager_voting, websocket)

    async def web_socket_results(self, websocket: WebSocket) -> None:
        await self._controller.ws_manager_results.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
                await self.refresh_active_poll_page()
        except WebSocketDisconnect:
            await self._handle_websocket_disconnect(self._controller.ws_manager_results, websocket)

    async def web_socket_admin(self, websocket: WebSocket) -> None:
        await self._controller.ws_manager_admin.connect(websocket)
        try:
            while True:
                json_data = await websocket.receive_json()
                if (active_poll := json_data.get("active_poll", False)) is False:
                    _logger.warning("Websocket got unknown data `%s`. Ignoring.", json_data)
                    continue

                if active_poll is None:
                    await self.make_idle()
                else:
                    await self.update_poll(active_poll)

                await self.refresh_admin_page()
                await self.refresh_active_poll_page()
        except WebSocketDisconnect:
            await self._handle_websocket_disconnect(self._controller.ws_manager_admin, websocket)
