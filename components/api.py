import json
import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Annotated, Literal

from fastapi import Cookie, HTTPException
from pydantic_core import ValidationError
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket, WebSocketDisconnect

from components.objects import Poll, PollCookie, PollVote

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
        self._controller.fast_api.websocket("/websocket")(self.web_socket)
        self._controller.fast_api.get("/")(self.static_page)

    def static_page(
        self, request: Request, poll_votes: Annotated[str | None, Cookie()] = None
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

    async def get_active_poll(self) -> Poll:
        if self._controller.active_poll is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No active poll")
        return self._controller.active_poll

    async def make_idle(self) -> Literal[True]:
        await self._controller.stop_active_poll()
        return True

    async def update_poll(self, poll: Poll | str) -> Literal[True]:
        await self._controller.update_active_poll(poll)
        return True

    async def _handle_websocket_disconnect(self, websocket: WebSocket) -> None:
        await self._controller.websocket_manager.disconnect(websocket)

    async def _handle_websocket_add_poll_vote(self, poll_vote: PollVote) -> None:
        await self._controller.add_poll_vote(poll_vote)

    async def web_socket(self, websocket: WebSocket) -> None:
        await self._controller.websocket_manager.connect(websocket)
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
            await self._handle_websocket_disconnect(websocket)
