import json
import typing as t
from .._types import SessionSerializer


class JSONSerializer(SessionSerializer):

    def encode(self, data: t.Dict[t.Any, t.Any]) -> bytes:
        return json.dumps(data).encode()

    def decode(self, data: bytes) -> t.Dict[t.Any, t.Any]:
        return t.cast(t.Dict[t.Any, t.Any], json.loads(data))
