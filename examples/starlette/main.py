import os
import typing as t

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.endpoints import HTTPEndpoint
from starlette.types import ASGIApp

from auth1 import (
    SessionManager,
    AuthManager,
    Guard,
    SessionGuard,
    UserProvider,
    StatefullGuard
)

from .middleware import SessionMiddleware, AuthenticateMiddleware
from .session import FileSessionHandler, create_file_session_handler
from .user import NoopUserProvider1

async def dashboard(request: Request):
    # request.session['horas'] = "Hello world"
    # request.session['foo'] = ["abc", "def", "hello"]
    # request.session['123'] = "34567"
    # request.session['test1'] = {
    #     'local1': "asa denggan sude",
    #     'local2': 355
    # }
    print(f"request.user: {request.user}")
    return Response("Hello world")

class LoginEndpoint(HTTPEndpoint):

    async def get(self, request: Request):
        return Response("Render Login Form Here")

    async def post(self, request: Request):
        form = await request.form()

        username: str = form['username']
        password: str = form['password']

        credentials: t.Dict[str, t.Any] = {'username': username, 'password': password}

        guard = self._get_statefull_guard(request)

        attempt_result = guard.attempt(credentials)

        print(f"attempt_result: {attempt_result}")

        return Response("Hello world login")

    def _get_statefull_guard(self, request: Request) -> StatefullGuard:
        guard: StatefullGuard = auth_manager.guard()
        if hasattr(guard, "set_session"):
            guard.set_session(request.session)
        return guard

session_config = {
    'cookie': "starlette_example"
}

auth_config = {
    'defaults': {
        'guard': "web"
    },
    'guards': {
        'web': {
            'driver': "session"
        }
    }
}

session_manager: SessionManager = SessionManager(session_config)

@session_manager.handler_factory("file")
def file_session_handler() -> FileSessionHandler:
    return create_file_session_handler()

auth_manager: AuthManager = AuthManager(auth_config)

@auth_manager.factory("session")
def session_guard_factory(name: str) -> Guard:
    return SessionGuard(name, NoopUserProvider1())

routes = [
    Route(
        "/",
        dashboard,
        methods=["GET"],
        middleware=[
            Middleware(SessionMiddleware, session_manager),
            Middleware(AuthenticateMiddleware, auth_manager, redirect_to="/login")
        ]
    ),
    Route("/login", LoginEndpoint, middleware=[
        Middleware(SessionMiddleware, session_manager)
    ])
]

app = Starlette(routes=routes)

if __name__ == "__main__":
    from starlette.testclient import TestClient

    client = TestClient(app)
    response = client.get(
        "/",
        headers={'Cookie': "starlette_example=bc61e642aa1394a4e48f390e6d7f944f565be2ff"},
        # follow_redirects=False
    )
    # response = client.post(
    #     "/login",
    #     headers={'Cookie': "starlette_example=0d7e7954da7d332ce6498ccc7bdc49894318ef61"},
    #     # follow_redirects=False
    #     data={
    #         'username': "harianja",
    #         'password': "Harianja710433!"
    #     }
    # )

    print(f"response: {response.content}")
    print(f"response: {response.cookies}")
