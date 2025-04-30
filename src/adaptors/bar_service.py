from dataclasses import dataclass
from core.ports.bar_service import BarService
from core.domain.bar import Bar
from core.ports.bar_service import WrongInputParametresException, InvalidDateRangeException
from datetime import datetime


@dataclass
class BarServiceAdaptor(BarService):
    async def get_bar(self, symbol: str | None, start_date: str | None, end_date: str | None) -> Bar:
        if symbol is None:
            raise WrongInputParametresException(message="Symbol is required")
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
        current_date = datetime.now()

        if start_date_in_datetime > current_date or end_date_in_datetime > current_date:
            raise InvalidDateRangeException(message="Date must be in past or present time")
        delta = end_date_in_datetime - start_date_in_datetime
        
         
        if delta.days > 30:
            raise InvalidDateRangeException(message=f"Date must be not over 1 month")
        if delta.days < 0:
            raise InvalidDateRangeException(message=f"start_date must be lower than end_date")
        


        
        async with self.barclient as client:
            response = await client.get_bar(symbol=symbol, start_date=start_date, end_date=start_date)
            return response