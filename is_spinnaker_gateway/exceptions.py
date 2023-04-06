from is_wire.core import Status, StatusCode


class StatusException(Exception):

    def __init__(self, code: StatusCode, message: str):
        self.message = message
        self.status = Status(code=code, why=message)
        super().__init__(self.message)
