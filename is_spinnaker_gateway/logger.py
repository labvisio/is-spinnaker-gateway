import sys
import logging

from typing import Callable, Any

from is_wire.core.utils import assert_type
from colorlog import ColoredFormatter, StreamHandler, getLogger


class Logger:

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARN
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, name: str, level: int = logging.DEBUG):
        assert_type(name, str, "name")

        style = "%(log_color)s[%(levelname)-.1s][%(threadName)s]" \
                "[%(asctime)s][%(name)s] %(message)s"

        formatter = ColoredFormatter(
            style,
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'white,bg_red',
            },
            secondary_log_colors={},
            style='%')

        self.logger = getLogger(name)
        self.logger.propagate = False

        if len(self.logger.handlers) == 0 and name:
            handler = StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.set_level(level)

        self.has_callback = False

    def set_critical_callback(self, callback: Callable[[Any], None]):
        self.has_callback = True
        self.callback = callback

    def set_level(self, level: int):
        self.logger.setLevel(level)

    def debug(self, formatter: str, *args):
        self.logger.debug(formatter.format(*args))

    def info(self, formatter: str, *args):
        self.logger.info(formatter.format(*args))

    def warn(self, formatter: str, *args):
        self.logger.warning(formatter.format(*args))

    def error(self, formatter: str, *args):
        self.logger.error(formatter.format(*args))

    def critical(self, formatter: str, *args, **kwargs):
        self.logger.critical(formatter.format(*args))
        if self.has_callback:
            self.callback(**kwargs)
        sys.exit(-1)
