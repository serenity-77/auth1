import typing as t
from ._types import AuthFactory, Guard

# config = {
#     'defaults': {
#         'guards': 'web'
#     },
#
#     'guards': {
#         'web': {
#             'driver': 'session',
#             'factory': ...
#         }
#     }
# }

class AuthManager(AuthFactory):

    def __init__(self, config: t.Dict[str, t.Any]):
        self._config = config
        self._driver_factory: t.Dict[str, t.Callable] = {} #type: ignore [type-arg]

    @property
    def config(self) -> t.Dict[str, t.Any]:
        return self._config

    def guard(self, name: str | None = None) -> Guard | None:
        if name is None:
            name = self._get_default_driver()

        guard_config = self._config['guards'][name]
        driver_name = guard_config['driver']

        driver_factory = self._driver_factory[driver_name]

        guard: Guard | None = driver_factory(name)

        return guard

    def factory(self, name: str) -> t.Callable: # type: ignore [type-arg]
        def decorator(f: t.Callable) -> t.Callable: # type: ignore [type-arg]
            self._driver_factory[name] = f
            return f
        return decorator

    def _get_default_driver(self) -> str:
        try:
            defaults = self._config['defaults']
        except KeyError:
            defaults = {}

        if isinstance(defaults, dict):
            try:
                return defaults['guard'] # type: ignore
            except KeyError:
                pass

        raise RuntimeError("No default guard specified")
