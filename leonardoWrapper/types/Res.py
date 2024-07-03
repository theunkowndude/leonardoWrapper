import sys
from typing import TypedDict

sys.dont_write_bytecode = True


class DefaultResponseType(TypedDict):
    status_code: int
    text: str
    json: dict