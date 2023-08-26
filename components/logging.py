import logging
from logging.handlers import RotatingFileHandler


def setup_logging(debug_mode: bool = False) -> None:
    params = {
        "format": "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        "datefmt": "%Y-%m-%dT%H:%M:%S",
        "level": logging.WARNING,
    }
    if debug_mode:
        params["level"] = logging.INFO
    else:
        params["handlers"] = [
            RotatingFileHandler("./live_poll.log", maxBytes=100000, backupCount=10)
        ]

    logging.basicConfig(**params)  # type: ignore
