import typing as t
from .._types import SessionHandler, SessionSerializer
from ._store import SessionStore

class SessionManager:

    def __init__(self, config: t.Dict[str, t.Any]):
        self._config = config
        self._handler_factory: t.Dict[str, t.Callable] = {} # type: ignore[type-arg]
        self._serializer_factory: t.Dict[str, t.Callable] = {} # type: ignore[type-arg]

    @property
    def config(self) -> t.Dict[str, t.Any]:
        return self._config

    def create(self, name: str) -> SessionStore:
        session_name: str = "PHPSESSID"

        try:
            session_name = self._config['cookie']
        except KeyError:
            pass

        if not session_name:
            session_name = "PHPSESSID"

        handler = self._create_handler(name)

        serializer_name = self._config.get("serializer", None)

        serializer = self._create_serializer(serializer_name)

        session_store: SessionStore = SessionStore(session_name, handler, id=None, serializer=serializer)

        return session_store

    def handler_factory(self, name: str) -> t.Callable: # type: ignore [type-arg]
        def decorator(f: t.Callable) -> t.Callable: # type: ignore [type-arg]
            self._handler_factory[name] = f
            return f
        return decorator

    def serializer_factory(self, name: str) -> t.Callable: # type: ignore [type-arg]
        def decorator(f: t.Callable) -> t.Callable: # type: ignore [type-arg]
            self._serializer_factory[name] = f
            return f
        return decorator

    def _create_handler(self, name: str) -> SessionHandler:
        handler_factory = self._handler_factory[name]
        handler: SessionHandler = handler_factory()
        return handler

    def _create_serializer(self, name: str | None) -> SessionSerializer | None:
        if name is None:
            return None
        serializer_factory = self._serializer_factory[name]
        serializer: SessionSerializer = serializer_factory()
        return serializer
