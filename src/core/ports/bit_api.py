from dataclasses import dataclass
import aiohttp
from abc import ABC, abstractmethod
from .errors import ServiceLayerException


@dataclass
class BadRequestException(ServiceLayerException):
    pass


@dataclass
class ServerErrorException(ServiceLayerException):
    pass


@dataclass
class NotAuthorisedException(ServiceLayerException):
    pass



@dataclass
class BarAPI(ABC):
    endpoint_url: str
    auth_key: str
    session: aiohttp.ClientSession | None = None

    @abstractmethod
    async def __aenter__(self) -> "BarAPI":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        raise NotImplementedError

    @abstractmethod
    async def get_bar(self, symbol: str, start_date: str, end_date: str) -> dict:
        raise NotImplementedError
