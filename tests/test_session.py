import pytest
import typing as t
import json
import copy

from auth1 import (
    Session,
    SessionStore,
    SessionHandler,
    NullSessionHandler,
    SessionSerializer,
    JSONSerializer,
    SessionManager
)

from ._helpers import (
    NoopSessionHandler,
    NoopSaveSessionHandler,
    NoopReadSessionHandler
)

def test_session_handler() -> None:
    handler: SessionHandler = NullSessionHandler()

    assert isinstance(handler, SessionHandler)
    assert isinstance(handler, NullSessionHandler)

def test_session_json_serializer() -> None:
    serializer: SessionSerializer = JSONSerializer()

    assert isinstance(serializer, SessionSerializer)
    assert isinstance(serializer, JSONSerializer)

    data: bytes = b'{"hello": "world", "init": [1, 2, 3]}'

    decoded = serializer.decode(data)
    assert decoded == {'hello': "world", 'init': [1, 2, 3]}

    encoded = serializer.encode(decoded)
    assert encoded == data

class NoopSerializer(SessionSerializer):

    def encode(self, data: t.Dict[t.Any, t.Any]) -> bytes:
        return b""

    def decode(self, data: bytes) -> t.Dict[t.Any, t.Any]:
        return {}


def test_session_store_default_init() -> None:
    session_store: Session = SessionStore("auth1", NullSessionHandler())

    assert isinstance(session_store, Session)
    assert isinstance(session_store, SessionStore)
    assert "auth1" == session_store.name
    assert isinstance(session_store.handler, SessionHandler)
    assert isinstance(session_store.handler, NullSessionHandler)
    assert session_store.id is None
    assert isinstance(session_store.serializer, SessionSerializer)
    assert isinstance(session_store.serializer, JSONSerializer)

    assert {} == session_store._attributes

    session_store['data1'] = "session 1"

    assert "session 1" == session_store['data1']

    with pytest.raises(AttributeError) as exc_info:
        session_store['data2']

    assert "SessionStore object has no attribute `data2`" == exc_info.value.args[0]

@pytest.mark.asyncio
async def test_session_store_async_migrate() -> None:
    def session_store_id() -> str:
        return "54321"

    handler = NoopSessionHandler(_async=True)

    session_store: Session = SessionStore("auth1", handler, id="12345")
    setattr(session_store, "generate_session_id", session_store_id)

    migrate_result: bool = await session_store.async_migrate(True)

    assert True == migrate_result
    assert "54321" == session_store.id

    assert True == handler.destroyed


def test_session_store_set_id() -> None:
    def session_store_id() -> str:
        return "54321"

    handler = NoopSessionHandler(_async=True)

    session_store: Session = SessionStore("auth1", handler)
    setattr(session_store, "generate_session_id", session_store_id)

    assert session_store.id is None

    session_store.id = None

    assert "54321" == session_store.id


def test_session_store_save() -> None:
    session_data: t.Dict[str, t.Any] = {
        'key1': "hello World",
        'key2': {
            'key1': "value1",
            'key2': 55
        }
    }

    encoded_session_data: bytes = json.dumps(session_data).encode()

    handler = NoopSaveSessionHandler()

    session_store: Session = SessionStore("auth1", handler, id="12345")

    for k, v in session_data.items():
        session_store[k] = v

    session_store.save()

    assert encoded_session_data == handler.saved_data
    assert "12345" == handler.saved_id


@pytest.mark.asyncio
async def test_session_async_save() -> None:
    session_data: t.Dict[str, t.Any] = {
        'key1': "hello World",
        'key2': {
            'key1': "value1",
            'key2': 55
        }
    }

    encoded_session_data: bytes = json.dumps(session_data).encode()

    handler = NoopSaveSessionHandler(_async=True)
    session_store: Session = SessionStore("auth1", handler, id="12345")

    for k, v in session_data.items():
        session_store[k] = v

    await session_store.async_save()

    assert encoded_session_data == handler.saved_data
    assert "12345" == handler.saved_id

def test_session_start() -> None:
    session_data: t.Dict[str, t.Any] = {
        'key1': "hello World",
        'key2': {
            'key1': "value1",
            'key2': 55
        }
    }

    token: t.List[str] = ["abcdef", "ghijkl"];

    def generate_token() -> str:
        return token.pop(0)

    encoded_session_data: bytes = json.dumps(session_data).encode()

    handler: SessionHandler = NoopReadSessionHandler(encoded_session_data)

    session_store: SessionStore = SessionStore("auth1", handler, id="12345")

    setattr(session_store, "_generate_token", generate_token)

    session_store.start()

    assert "abcdef" == session_store.token

    session_data['_token'] = "abcdef"
    assert session_data == session_store._attributes

    assert isinstance(handler, NoopReadSessionHandler)
    assert "12345" == handler.read_id

    handler = NoopSessionHandler()
    session_store = SessionStore("auth1", handler, id="12345")

    setattr(session_store, "_generate_token", generate_token)

    session_store.start()

    assert "ghijkl" == session_store.token
    assert {'_token': "ghijkl"} == session_store._attributes


@pytest.mark.asyncio
async def test_session_async_start() -> None:
    session_data: t.Dict[str, t.Any] = {
        'key1': "hello World",
        'key2': {
            'key1': "value1",
            'key2': 55
        }
    }

    token: t.List[str] = ["abcdef", "ghijkl"];

    def generate_token() -> str:
        return token.pop(0)

    encoded_session_data: bytes = json.dumps(session_data).encode()

    handler: SessionHandler = NoopReadSessionHandler(encoded_session_data, _async=True)

    session_store: SessionStore = SessionStore("auth1", handler, id="12345")

    setattr(session_store, "_generate_token", generate_token)

    await session_store.async_start()

    assert "abcdef" == session_store.token

    session_data['_token'] = "abcdef"
    assert session_data == session_store._attributes

    assert isinstance(handler, NoopReadSessionHandler)
    assert "12345" == handler.read_id

    handler = NoopSessionHandler()

    session_store = SessionStore("auth1", handler, id="12345")
    setattr(session_store, "_generate_token", generate_token)

    await session_store.async_start()

    assert "ghijkl" == session_store.token
    assert {'_token': "ghijkl"} == session_store._attributes


_CONFIG: t.Dict[str, t.Any] = {
    'serializer': "noop",
    'cookie': "auth1_session"
}


def test_session_manager_init() -> None:
    session_manager = SessionManager(_CONFIG)
    assert isinstance(session_manager, SessionManager)
    assert _CONFIG == session_manager._config

def test_session_manager_create_session() -> None:
    config = copy.deepcopy(_CONFIG)

    session_manager = SessionManager(config)

    @session_manager.handler_factory("null")
    def null_handler_factory() -> NullSessionHandler:
        return NullSessionHandler()

    @session_manager.serializer_factory("noop")
    def noop_serializer_factory() -> NoopSerializer:
        return NoopSerializer()

    assert "null" in session_manager._handler_factory

    session_store: SessionStore = session_manager.create("null")

    assert isinstance(session_store, SessionStore)
    assert "auth1_session" == session_store.name
    assert session_store.id is None
    assert isinstance(session_store._handler, NullSessionHandler)
    assert isinstance(session_store._serializer, NoopSerializer)

    del config['serializer']

    session_manager = SessionManager(config)

    @session_manager.handler_factory("null")
    def null_handler_factory1() -> NullSessionHandler:
        return NullSessionHandler()

    session_store = session_manager.create("null")

    assert isinstance(session_store._serializer, JSONSerializer)

    del config['cookie']

    session_manager = SessionManager(config)

    @session_manager.handler_factory("null")
    def null_handler_factory2() -> NullSessionHandler:
        return NullSessionHandler()

    session_store = session_manager.create("null")

    assert "PHPSESSID" == session_store.name
