import logging
from is_wire.core import Logger as WireLogger


class Logger(WireLogger):

    def __init__(self, name: str, level: int = logging.DEBUG):
        super().__init__(name=name, level=level)
        self.logger.propagate = False
