from dataclasses import dataclass
from core.ports.bar_service import BarService
from core.domain.bar import Bar
from core.domain.forecast import Forecast
from core.ports.bar_service import (
    WrongInputParametresException,
    InvalidDateRangeException,
    InvalidTargetInterval,
    ServiceLayerException,
    InvalidHistoryBars
)
from datetime import datetime, timedelta
from pydantic import ValidationError
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression


@dataclass
class BarServiceAdaptor(BarService):
    async def get_bar(
        self, symbol: str | None, start_date: str | None, end_date: str | None
    ) -> Bar:
        if symbol is None:
            raise WrongInputParametresException(code="MissingSymbol", message="Symbol is required")
        if start_date is None:
            raise WrongInputParametresException(
                code="MissingDate", message="Missing required parameter: start_date"
            )

        date_format = "%Y-%m-%d"
        if end_date is None:
            end_date = datetime.strftime(datetime.now(), date_format)
        try:
            start_date_in_datetime = datetime.strptime(start_date, date_format)
            end_date_in_datetime = datetime.strptime(end_date, date_format)
        except ValueError as e:
            raise InvalidDateRangeException(
                code="InvalidTimeParameter",
                message=f"Wrong date format, use {date_format}"
            )
        except Exception as e:
            raise e
        current_date = datetime.now()

        if start_date_in_datetime > current_date or end_date_in_datetime > current_date:
            raise InvalidDateRangeException(
                code="InvalidDateRange",
                message="Date must be in past or present time"
            )
        delta = end_date_in_datetime - start_date_in_datetime

        if delta.days > 30:
            raise InvalidDateRangeException(code="InvalidDateRange", message=f"Date must be not over 1 month")
        if delta.days < 0:
            raise InvalidDateRangeException(
                code="StartDateAfterEndDate",
                message=f"Start date must be earlier than end date"
            )

        async with self.barclient as client:
            response = await client.get_bar(
                symbol=symbol, start_date=start_date, end_date=end_date
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
            raise InvalidTargetInterval(code="InvalidTargetInterval", message="Interval must be greater than zero and a multiple of 5")
        elif target_interval % 5 != 0:
            raise InvalidTargetInterval(code="InvalidTargetInterval", message="Interval must be greater than zero and a multiple of 5")

        bars: list[dict] = await self.get_bar(
            symbol=symbol, start_date=start_date, end_date=end_date
        )
        num_of_minimum_data = target_interval // 5
        num_of_source_bars = len(bars) - (len(bars) % num_of_minimum_data)
        if num_of_source_bars <= 0:
            raise InvalidTargetInterval("Not enougth info for chose interval")

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
    



    async def forecast(self, symbol, interval, start_forecast_datetime, history_bars):
        if datetime.strptime(start_forecast_datetime, "%Y-%m-%dT%H:%M:%S.%fZ") > datetime.now():
            raise InvalidHistoryBars(code="InvalidStartForecastDatetime", message="Forecast datetime can not be in future")
        
        try:
            interval = int(interval)
        except Exception as e:
            raise InvalidHistoryBars(code="InvalidTargetInterval", message="Interval must be greater than zero and a multiple of 5")
        
        if history_bars <= 1:
            raise InvalidHistoryBars(code="InvalidHistoryBars", message="History bars must be a positive integer")

        start_forecast_datetime_time = datetime.strptime(start_forecast_datetime.split('T')[0], "%Y-%m-%d")
        bars = await self.get_aggregated_bar(
            symbol=symbol,
            target_interval=interval,
            start_date=datetime.strftime(start_forecast_datetime_time - timedelta(days=29), "%Y-%m-%d"),
            end_date=datetime.strftime(start_forecast_datetime_time, "%Y-%m-%d")
        )
        
        required_bars = history_bars + 1
        if len(bars) < required_bars:
            raise InvalidHistoryBars(code="NotEnoughData", message=f"Need at least {required_bars} bars, got {len(bars)}")
        
        history = bars[-required_bars:]
        
        df = pd.DataFrame([{
            'datetime': datetime.strptime(bar['datetime'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            'open': bar['open'],
            'high': bar['high'],
            'low': bar['low'],
            'close': bar['close']
        } for bar in history]).sort_values('datetime')
        


        df['range'] = df['high'] - df['low']

        average_range = df['range'].mean()
        half_average_range = average_range / 2
        for i in range(1, history_bars + 1):
            df[f'close_lag_{i}'] = df['close'].shift(i)
        
        df.dropna(inplace=True)
        
        if len(df) == 0:
            raise InvalidHistoryBars(code="EmptyDataset", message="Not enough data after creating lags")
        X = df[[f'close_lag_{i}' for i in range(1, history_bars + 1)]]
        y = df['close']
        print(X)
        
        
        model = LinearRegression()
        model.fit(X, y)
        
        last_data = X.iloc[-1:].values.reshape(1, -1)
        forecast_price = model.predict(last_data)[0]
        
        residuals = y - model.predict(X)
        std_dev = residuals.std()
        upper_bound = forecast_price + half_average_range
        lower_bound = forecast_price - half_average_range
        
        current_price = df['close'].iloc[-1]
        if forecast_price > current_price: 
            recommendation = "BUY"
        elif forecast_price <= current_price: 
            recommendation = "SELL"
        

        print({
            "recommendation": recommendation,
            "forecast_price": round(forecast_price, 2),
            "upper_bound": round(upper_bound, 2),
            "lower_bound": round(lower_bound, 2)
        })
        return {
            "recommendation": recommendation,
            "forecast_price": round(forecast_price, 2),
            "upper_bound": round(upper_bound, 2),
            "lower_bound": round(lower_bound, 2)
        }

