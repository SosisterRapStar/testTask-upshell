from fastapi import APIRouter, Header, HTTPException, Request
from core.domain.bar import Bar
from core.domain.forecast import Forecast
from core.ports.bar_service import (
    BarService,
    InvalidDateRangeException,
    WrongInputParametresException,
    InvalidTargetInterval
)
from core.ports.errors import ServiceLayerException
from core.ports.bit_api import (
    NotAuthorisedException,
    BadRequestException,
    ServerErrorException,
)
from fastapi.responses import JSONResponse
from fastapi import status

router = APIRouter(tags=["Bar"])


# TODO: сделать отдельные классы для 400 ошибок, для 500 и от них наследовать
def check_error(e: Exception):
    if isinstance(e, BadRequestException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"errorCode": "InvalidSymbol", "message": "Symbol is invalid"},
        )

    if isinstance(e, NotAuthorisedException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"errorCode": "NotAuthorized", "message": e.message},
        )

    if isinstance(e, InvalidDateRangeException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"errorCode": e.code, "message": e.message},
        )

    if isinstance(e, WrongInputParametresException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"errorCode": e.code, "message": e.message},
        )
    
    if isinstance(e, InvalidTargetInterval):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "errorCode": e.code,
                "message": e.message
            }
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "statusCode": "InternalError",
            "message": "Internal server error",
        },
    )


@router.get("/history", response_model=list[Bar])
async def get_bar(
    request: Request,
    symbol: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    container = request.app.state.container
    bar_service: BarService = container.bar_service
    try:
        result = await bar_service.get_bar(symbol, start_date, end_date)
        return result
    except Exception as e:
        return check_error(e)


@router.get("/aggregate", response_model=list[Bar])
async def get_aggregated_bar(
    request: Request,
    symbol: str | None = None,
    target_interval: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    container = request.app.state.container
    bar_service: BarService = container.bar_service
    try:
        result = await bar_service.get_aggregated_bar(symbol=symbol, start_date=start_date, end_date=end_date, target_interval=target_interval)
        return result
    except Exception as e:
        return check_error(e)
    


@router.get("/forecast", response_model=Forecast)
async def get_aggregated_bar(
    request: Request,
    symbol: str | None = None,
    interval: int | None = None,
    start_forecast_datetime: str | None = None,
    history_bars: str | None = None,
):
    container = request.app.state.container
    bar_service: BarService = container.bar_service
    try:
        print("dsdd")
        result = await bar_service.forecast(symbol=symbol, interval=interval, start_forecast_datetime=start_forecast_datetime, history_bars=history_bars)
        return result
    except Exception as e:
        return check_error(e)