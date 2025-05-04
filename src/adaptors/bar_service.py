from dataclasses import dataclass
from core.ports.bar_service import BarService
from core.domain.bar import Bar
from core.ports.bar_service import (
    WrongInputParametresException,
    InvalidDateRangeException,
    InvalidTargetInterval,
    ServiceLayerException,
)
from datetime import datetime
from pydantic import ValidationError


@dataclass
class BarServiceAdaptor(BarService):
    async def get_bar(
        self, symbol: str | None, start_date: str | None, end_date: str | None
    ) -> Bar:
        if symbol is None:
            raise WrongInputParametresException(message="symbol is required")
        if start_date is None:
            raise WrongInputParametresException(
                message="missing required parameter: start_date"
            )

        date_format = "%Y-%m-%d"
        if end_date is None:
            end_date = datetime.strftime(datetime.now(), date_format)
        try:
            start_date_in_datetime = datetime.strptime(start_date, date_format)
            end_date_in_datetime = datetime.strptime(end_date, date_format)
        except ValueError as e:
            raise InvalidDateRangeException(
                message=f"wrong date format, use {date_format}"
            )
        except Exception as e:
            raise e
        current_date = datetime.now()

        if start_date_in_datetime > current_date or end_date_in_datetime > current_date:
            raise InvalidDateRangeException(
                message="date must be in past or present time"
            )
        delta = end_date_in_datetime - start_date_in_datetime

        if delta.days > 30:
            raise InvalidDateRangeException(message=f"date must be not over 1 month")
        if delta.days < 0:
            raise InvalidDateRangeException(
                message=f"start_date must be lower than end_date"
            )

        async with self.barclient as client:
            response = await client.get_bar(
                symbol=symbol, start_date=start_date, end_date=start_date
            )
            return response

    async def get_aggregated_bar(
        self,
        symbol: str | None,
        target_interval: int | None,
        start_date: str | None,
        end_date: str | None,
    ):
        if target_interval < 0:
            raise InvalidTargetInterval("target interval can not be lower than 0")
        elif target_interval % 5 != 0:
            raise InvalidTargetInterval("target interval must be divisible by 5")

        bars: list[dict] = await self.get_bar(
            symbol=symbol, start_date=start_date, end_date=end_date
        )
        num_of_minimum_data = target_interval // 5
        num_of_source_bars = len(bars) - (len(bars) % num_of_minimum_data)
        if num_of_source_bars <= 0:
            raise InvalidTargetInterval("not enougth info for chose interval")

        ans_bars = list()

        for group_start in range(0, len(bars), num_of_minimum_data):
            group_end = group_start + num_of_minimum_data
            if group_end > len(bars):
                break  
            

            new_low = bars[group_start]["low"]  
            new_high = bars[group_start]["high"] 
            for i in range(group_start, group_end):
                new_low = min(bars[i]["low"], new_low)
                new_high = max(bars[i]["high"], new_high)
            
            aggregated_bar = {
                "datetime": bars[group_start]["datetime"],
                "open": bars[group_start]["open"],
                "high": new_high,
                "low": new_low,
                "close": bars[group_end - 1]["close"]
            }
            ans_bars.append(aggregated_bar)

        return ans_bars
