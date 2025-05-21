import typing as t

from auth1 import (
    UserProvider,
    AuthenticatableRetval,
    Authenticatable,
    SessionHandler
)

class NoopUserProvider1(UserProvider):

    def retrieve_by_id(self, id: str | int) -> AuthenticatableRetval:
        return None

    def retrieve_by_credentials(self, credentials: t.Dict[str, t.Any]) -> AuthenticatableRetval:
        return None

    def validate_credentials(self, user: Authenticatable, credentials: t.Dict[str, t.Any]) -> bool:
        return True


class NoopSessionHandler(SessionHandler):
    destroyed: bool = False

    def __init__(self, _async: bool = False):
        self._async = _async

    def read(self, id: str) -> t.Awaitable[bytes] | bytes:
        return b""

    def write(self, id: str, data: bytes) -> t.Awaitable[None] | None:
        return None

    def destroy(self, id: str) -> t.Awaitable[None] | None:
        if self._async:
            return self._async_destroy(id)
        self.destroyed = True
        return None

    async def _async_destroy(self, id: str) -> None:
        self.destroyed = True


class NoopSaveSessionHandler(NoopSessionHandler):

    saved_data: bytes = b""
    saved_id: str = ""

    def write(self, id: str, data: bytes) -> t.Awaitable[None] | None:
        if self._async:
            return self._async_write(id, data)
        self.saved_data = data
        self.saved_id = id
        return None

    async def _async_write(self, id: str, data: bytes) -> None:
        self.saved_data = data
        self.saved_id = id
        return None


class NoopReadSessionHandler(NoopSaveSessionHandler):

    read_id: str = ""

    def __init__(self, data: bytes, _async: bool = False) -> None:
        self._data = data
        super().__init__(_async)

    def read(self, id: str) -> t.Awaitable[bytes] | bytes:
        self.read_id = id
        return self._data
