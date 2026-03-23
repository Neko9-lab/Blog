from pydantic import BaseModel


class LogQuery(BaseModel):
    lines: int = 100
