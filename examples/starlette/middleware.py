from http.cookies import SimpleCookie

from starlette.types import (
    ASGIApp,
    Scope,
    Receive,
    Send,
    Message
)

from starlette.requests import HTTPConnection
from starlette.datastructures import MutableHeaders
from starlette.responses import RedirectResponse

from auth1 import (
    SessionManager,
    SessionStore,
    AuthManager,
    Guard
)

class SessionMiddleware:

    def __init__(self, app: ASGIApp, session_manager: SessionManager) -> None:
        self.app = app
        self.session_manager = session_manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        http_conn = HTTPConnection(scope)

        session_store = self._create_session(http_conn)

        await session_store.async_start()

        scope['session'] = session_store

        async def _send(message: Message):
            if message['type'] == "http.response.start":
                headers = MutableHeaders(scope=message)
                self._add_cookie_to_response(session_store, http_conn, headers)

            await session_store.async_save()

            await send(message)

        await self.app(scope, receive, _send)

    def _add_cookie_to_response(self, session_store: SessionStore, http_conn: HTTPConnection, headers: MutableHeaders) -> None:
        cookie_config = self.session_manager.config.get("cookie_params", {})

        session_cookie = session_store.name
        cookie = SimpleCookie()

        cookie[session_cookie] = session_store.id
        cookie[session_cookie]['path'] = cookie_config.get("path", "/")
        cookie[session_cookie]['expires'] = cookie_config.get("expires", 2 * 60 * 60)
        cookie[session_cookie]['httponly'] = cookie_config.get("httponly", False)
        cookie[session_cookie]['samesite'] = cookie_config.get("samesite", "lax")
        cookie[session_cookie]['secure'] = http_conn.url.scheme == "https"

        domain = cookie_config.get("domain", None)

        if domain is not None:
            cookie[session_cookie]['domain'] = domain

        headers['Set-Cookie'] = cookie[session_cookie].OutputString()

    def _create_session(self, http_conn: HTTPConnection) -> SessionStore:
        session_store = self.session_manager.create("file")
        session_store.id = http_conn.cookies.get(session_store.name, None)
        return session_store


class AuthenticateMiddleware:

    def __init__(self, app: ASGIApp, auth_manager: AuthManager, redirect_to: str | None = None) -> None:
        self.app = app
        self.auth_manager = auth_manager
        self.redirect_to = redirect_to

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        guard: Guard = self.auth_manager.guard()

        if hasattr(guard, "set_session"):
            guard.set_session(scope['session'])

        user: Authenticatable | None = await guard.async_user()

        if user is None:
            response = RedirectResponse(self.redirect_to)
            await response(scope, receive, send)
            return

        scope['user'] = user

        await self.app(scope, receive, send)
