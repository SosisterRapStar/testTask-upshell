from dataclasses import dataclass
from abc import ABC, abstractmethod
from core.domain.bar import Bar
from core.domain.forecast import Forecast
from core.ports.bit_api import BarAPI
from core.ports.errors import ServiceLayerException


@dataclass
class WrongInputParametresException(ServiceLayerException):
    pass


@dataclass
class InvalidDateRangeException(ServiceLayerException):
    pass


@dataclass
class InvalidTargetInterval(ServiceLayerException):
    pass


@dataclass
class BarService(ABC):
    barclient: BarAPI

    @abstractmethod
    async def get_bar(
        self, symbol: str | None, start_date: str | None, end_date: str | None
    ) -> Bar:
        raise NotImplementedError

    @abstractmethod
    async def get_aggregated_bar(
        self,
        symbol: str | None,
        target_interval: int | None,
        start_date: str | None,
        end_date: str | None,
    ) -> list[Bar]:
        raise NotImplementedError
    

    @abstractmethod
    async def forecast(
        self, 
        symbol: str | None,
        interval: int | None,
        start_forecast_datetime: int | None, 
        history_bars: int | None,
    ) -> Forecast:
        raise NotImplementedError