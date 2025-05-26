import os
import typing as t
from auth1 import SessionHandler

class FileSessionHandler(SessionHandler):

    def __init__(self, path: str) -> None:
        self.path = path

    def read(self, id: str) -> bytes:
        try:
            with self._open_file(id, "rb") as f:
                data = f.read()
                return data
        except FileNotFoundError:
            return b""

    def write(self, id: str, data: bytes) -> None:
        with self._open_file(id, "wb") as f:
            f.write(data)

    def destroy(self, id: str) -> None:
        path = os.path.join(self.path, id)
        try:
            os.remove(path)
        except:
            pass

    def _open_file(self, filename: str, mode: str) -> t.BinaryIO:
        path = os.path.join(self.path, filename)
        return open(path, mode)


def create_file_session_handler() -> FileSessionHandler:
    return FileSessionHandler(os.path.join(os.getcwd(), "examples/starlette/files"))
