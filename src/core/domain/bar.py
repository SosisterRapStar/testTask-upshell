from datetime import datetime
from pydantic import BaseModel


class Bar(BaseModel):
    datetime: datetime
    open: float
    high: float
    low: float
    close: float


async def some_future_bussiness_logic_method() -> BaseModel:
    pass
