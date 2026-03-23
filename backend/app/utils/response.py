from typing import Any


def success(data: Any) -> dict:
    return {"code": 200, "msg": "success", "data": data}


def error(code: int, msg: str) -> dict:
    return {"code": code, "msg": msg, "data": {}}
