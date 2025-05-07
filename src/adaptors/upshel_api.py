import aiohttp
from dataclasses import dataclass
from core.ports.bit_api import BarAPI
from config import logger
import sys
from core.ports.bit_api import (
    NotAuthorisedException,
    ServerErrorException,
    BadRequestException,
)
from core.ports.errors import ServiceLayerException


response_to_error: dict[int, ServiceLayerException] = {
    400: BadRequestException,
    401: NotAuthorisedException,
    500: ServerErrorException,
}


@dataclass
class UpshelAPI(BarAPI):
    async def __aenter__(self) -> "BarAPI":
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session and not self.session.closed:
            await self.session.close()
        if exc:
            logger.error(f"Exception occurred: {exc}")

    async def get_bar(self, symbol: str, start_date: str, end_date: str) -> dict:
        if not self.session:
            logger.fatal("Aiohttp client session was not provided")
            sys.exit(1)
        async with self.session.get(
            url=f"http://{self.endpoint_url}?symbol={symbol}&start_date={start_date}&end_date={end_date}",
            headers={"api-key": f"{self.auth_key}"},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as response:
            print(
                f"http://{self.endpoint_url}?symbol={symbol}&start_date={start_date}&end_date={end_date}"
            )
            response_data = await response.json()
            print("Статус", response_data, response.status)
            response_status = response.status
            if response_status in response_to_error:
                # print("ПАРИРУРИ", response_to_error[response_status](message=response_data['message']))
                raise response_to_error[response_status](
                    code="", message=response_data["message"]
                )
            response.raise_for_status()
            return response_data
