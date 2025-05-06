from pydantic import BaseModel


class Forecast(BaseModel):
    recommendation: str
    forecast_price: float
    upper_bound: float
    lower_bound: float
