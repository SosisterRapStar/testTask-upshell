from dataclasses import dataclass
from core.ports.bar_service import BarService
from core.domain.bar import Bar
from core.ports.bar_service import WrongInputParametresException, InvalidDateRangeException
from datetime import datetime


@dataclass
class BarServiceAdaptor(BarService):
    async def get_bar(self, symbol: str | None, start_date: str | None, end_date: str | None) -> Bar:
        if symbol is None:
            raise WrongInputParametresException(message="Missing required parameter: symbol")
        if start_date is None:
            raise WrongInputParametresException(message="Missing required parameter: start_date")
        
        date_format = "%Y-%m-%d"

        if end_date is None:
            end_date = datetime.strftime(datetime.now(), date_format)
        try:
            start_date_in_datetime = datetime.strptime(start_date, date_format)
            end_date_in_datetime = datetime.strptime(end_date, date_format)
        except ValueError as e:
            raise InvalidDateRangeException(message=f"Wrong date format, use {date_format}")
        except Exception as e:
            raise e
        
        delta = end_date_in_datetime - start_date_in_datetime
        
        if delta.days > 30:
            raise InvalidDateRangeException(message=f"Wrong date range. Date range can not be bigger then 30 days")
        if delta.days < 0:
            raise InvalidDateRangeException(message=f"Wrong date format. End date can not be bigger then start_date")
        


        
        async with self.barclient as client:
            response = await client.get_bar(symbol=symbol, start_date=start_date, end_date=start_date)
            return response