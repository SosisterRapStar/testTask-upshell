from dataclasses import dataclass
from core.ports.bit_api import BarAPI


@dataclass
class FakeUpshelAPI(BarAPI):

    async def __aenter__(self) -> "BarAPI":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


    def set_fake_data(self, data):
        self.fake_data = data

    async def get_bar(
        self, symbol: str = None, start_date: str = None, end_date: str = None
    ) -> dict:
        return self.fake_data
