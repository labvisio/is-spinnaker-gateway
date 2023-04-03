import os

from is_wire.core import Logger as WireLogger

LOG_LEVELS = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL']
DEFAULT_LOG_LEVEL = 'INFO'


class Logger(WireLogger):

    def __init__(self, name: str):
        level = os.getenv('LOG_LEVEL', DEFAULT_LOG_LEVEL).upper()
        if level not in LOG_LEVELS:
            level = DEFAULT_LOG_LEVEL
        super().__init__(name=name, level=level)
        self.logger.propagate = False
