import logging
import logging.handlers

from fastapi_auth.core.config import DEBUG


class LevelFilter:
    def __init__(self, level):
        self._level = level

    def filter(self, log_record):
        return log_record.levelno == self._level


logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(message)s")

if DEBUG:
    log_info = logging.StreamHandler()
else:
    log_info = logging.handlers.RotatingFileHandler(
        "/var/log/web/users/info.log", maxBytes=1_000_000 * 10, backupCount=15
    )

log_info.addFilter(LevelFilter(logging.INFO))  # type: ignore

log_info.setFormatter(formatter)

logger.addHandler(log_info)
