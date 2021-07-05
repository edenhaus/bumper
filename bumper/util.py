import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from typing import MutableMapping

logformat = logging.Formatter(
    "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)d :: %(message)s"
)

__loggers: MutableMapping[str, logging.Logger] = {}
log_to_stdout = os.environ.get("LOG_TO_STDOUT")


def get_logger(name: str, rotate: RotatingFileHandler = None) -> logging.Logger:
    found_logger = __loggers.get(name)
    if found_logger:
        return found_logger

    logger = logging.getLogger(name)

    if not log_to_stdout:
        if not rotate:
            rotate = RotatingFileHandler(f"logs/{name}.log", maxBytes=5000000, backupCount=5)
            rotate.setFormatter(logformat)
        logger.addHandler(rotate)
    else:
        logger.addHandler(logging.StreamHandler(sys.stdout))

    __loggers[name] = logger

    if name == "mqttserver":
        get_logger("transitions", rotate).setLevel(logging.CRITICAL + 1)  # Ignore this logger
        get_logger("passlib", rotate).setLevel(logging.CRITICAL + 1)  # Ignore this logger
        get_logger("hbmqtt.broker", rotate)
        get_logger("hbmqtt.mqtt.protocol", rotate)
        get_logger("hbmqtt.client", rotate)

    return logger
