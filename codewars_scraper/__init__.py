from .scraper import Scraper
from loguru import logger as _logger
from sys import stdout as _stdout

_log_handlers = [
    {
        "sink": _stdout,
        "level": "INFO"
    },
    {
        "sink": "scraper.log",
        "level": "DEBUG",
        "rotation": "10 MB"
    }
]

_logger.configure(handlers=_log_handlers)
_logger.info(" ===== Initialized logger handlers ===== ")
