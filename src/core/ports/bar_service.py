from dataclasses import dataclass
from abc import ABC, abstractmethod
from core.domain.bar import Bar
from core.ports.bit_api import BarAPI
from core.ports.errors import ServiceLayerException


@dataclass
class WrongInputParametresException(ServiceLayerException):
    pass


@dataclass
class InvalidDateRangeException(ServiceLayerException):
    pass


@dataclass
class BarService(ABC):
    barclient: BarAPI

    @abstractmethod
    async def get_bar(self, symbol: str = None, minutes: int = None) -> Bar:
        raise NotImplementedError
