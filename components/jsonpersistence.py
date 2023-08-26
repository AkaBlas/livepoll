import asyncio
import json
import logging
from pathlib import Path

from components.objects import Poll

_LOGGER = logging.getLogger(__name__)


class JSONPersistence:
    def __init__(self, filepath: Path):
        self._filepath: Path = filepath
        self._polls: dict[str, Poll] = {}
        self.__lock = asyncio.Lock()

    async def initialize(self) -> None:
        if not self._filepath.exists():
            with self._filepath.open("w") as file:
                file.write("{}")

        with self._filepath.open("r") as file:
            try:
                polls = json.load(file)
            except json.JSONDecodeError as exc:
                _LOGGER.exception("Failed to load persistence file", exc_info=exc)
                polls = {}
            for poll_data in polls.values():
                poll = Poll(**poll_data)
                self._polls[poll.uid] = poll

    async def shutdown(self) -> None:
        await self.flush()

    async def get_polls(self) -> dict[str, Poll]:
        return {poll.uid: poll.model_copy(deep=True) for poll in self._polls.values()}

    async def _update_poll(self, poll: Poll) -> None:
        self._polls[poll.uid] = poll.model_copy(deep=True)

    async def update_poll(self, poll: Poll) -> None:
        await self._update_poll(poll)
        await self.flush()

    async def update_polls(self, polls: dict[str, Poll]) -> None:
        for poll in polls.values():
            await self._update_poll(poll)
        await self.flush()

    async def flush(self) -> None:
        async with self.__lock:
            await self.__flush()

    async def __flush(self) -> None:
        with self._filepath.open("w") as file:
            json.dump(
                {key: value.model_dump() for key, value in self._polls.items()}, file, indent=2
            )
