import asyncio
import logging
from pathlib import Path

from components.controller import Controller
from components.jsonpersistence import JSONPersistence
from components.logging import setup_logging

DEBUG_MODE = True


async def main() -> None:
    setup_logging(debug_mode=DEBUG_MODE)
    controller = Controller(
        persistence=JSONPersistence(Path("persistence.json")),
        debug_mode=DEBUG_MODE,
    )
    await controller.run(host="127.0.0.1", log_level=logging.INFO)


if __name__ == "__main__":
    asyncio.run(main())
