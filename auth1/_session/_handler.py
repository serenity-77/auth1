import typing as t
from .._types import SessionHandler

class NullSessionHandler(SessionHandler):

    destroyed: bool = False

    def read(self, id: str) -> bytes:
        return b""

    def write(self, id: str, data: bytes) -> None:
        return None

    def destroy(self, id: str) -> None:
        self.destroyed = True
