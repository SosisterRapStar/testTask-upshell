from dataclasses import dataclass
from core.ports.bit_api import BarAPI


@dataclass
class FakeUpshelAPI(BarAPI):
    fake_data: list[dict]
    async def __aenter__(self) -> "BarAPI":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get_bar(self, symbol: str, start_date: str, end_date: str) -> dict:
        return self.fake_data