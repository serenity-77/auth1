import os
import binascii
import typing as t
import inspect

from .._types import SessionHandler, SessionSerializer
from .._random import random_string
from ._serializer import JSONSerializer

class SessionStore:

    def __init__(
        self,
        name: str,
        handler: SessionHandler,
        id: str | None = None,
        serializer: SessionSerializer | None = None
    ):
        self._name = name
        self._handler: SessionHandler = handler
        self._id: str | None = id

        if serializer is None:
            serializer = JSONSerializer()

        self._serializer: SessionSerializer = serializer
        self._attributes: t.Dict[t.Any, t.Any] = {}

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def id(self) -> str | None:
        return self._id

    @id.setter
    def id(self, id: str | None) -> None:
        if id is None:
            id = self.generate_session_id()
        self._id = id

    @property
    def handler(self) -> SessionHandler:
        return self._handler

    @property
    def serializer(self) -> SessionSerializer:
        return self._serializer

    @property
    def token(self) -> str:
        return self._attributes['_token'] # type: ignore

    def start(self) -> None:
        assert self._id is not None

        session_data = self._handler.read(self._id)

        if inspect.isawaitable(session_data):
            raise TypeError("Cannot use awaitable return value from handler read")

        if not session_data:
            self._attributes = {}
        else:
            self._attributes = self._serializer.decode(session_data)

        if '_token' not in self._attributes:
            self.regenerate_token()

    async def async_start(self) -> None:
        assert self._id is not None

        session_data: t.Awaitable[bytes] | bytes = self._handler.read(self._id)

        if inspect.isawaitable(session_data):
            session_data = await session_data

        if not session_data:
            self._attributes = {}
        else:
            self._attributes = self._serializer.decode(session_data)

        if '_token' not in self._attributes:
            self.regenerate_token()

    def save(self) -> None:
        assert self._id is not None
        serialized = self._serializer.encode(self._attributes)
        self._handler.write(self._id, serialized)

    async def async_save(self) -> None:
        assert self._id is not None
        serialized = self._serializer.encode(self._attributes)
        write_result: t.Awaitable[None] | None = self._handler.write(self._id, serialized)

        if inspect.isawaitable(write_result):
            await write_result

    def migrate(self, destroy: bool = False) -> bool:
        if destroy and self._id is not None:
            self._handler.destroy(self._id)
        self._id = self.generate_session_id()
        return True

    async def async_migrate(self, destroy: bool = False) -> bool:
        if destroy and self._id is not None:
            destroy_result = self._handler.destroy(self._id)

            if inspect.isawaitable(destroy_result):
                await destroy_result

            self._id = self.generate_session_id()

        return True

    def generate_session_id(self) -> str:
        return random_string(40)

    def regenerate_token(self) -> None:
        self._attributes['_token'] = self._generate_token()

    def _generate_token(self) -> str:
        return random_string(40)

    def __getitem__(self, key: t.Any) -> t.Any:
        try:
            return self._attributes[key]
        except KeyError:
            raise AttributeError(f"{self.__class__.__name__} object has no attribute `{key}`")

    def __setitem__(self, key: t.Any, data: t.Any) -> None:
        self._attributes[key] = data
