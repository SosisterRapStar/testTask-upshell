from datetime import datetime
import pytest
from core.ports.bar_service import InvalidTargetInterval


@pytest.mark.parametrize("test_input, expected", [
    (
        [
            {"datetime": "2024-08-23T12:00:00Z", "open": 100, "high": 110, "low": 90, "close": 105},
            {"datetime": "2024-08-23T12:05:00Z", "open": 105, "high": 115, "low": 100, "close": 110}
        ],
        [
            {
                "datetime": "2024-08-23T12:00:00Z",
                "open": 100,
                "high": 115,  
                "low": 90,    
                "close": 110 
            }
        ]
    ),
    (
        [
            {"datetime": "2024-08-23T12:00:00Z", "open": 100, "high": 110, "low": 90, "close": 105},
            {"datetime": "2024-08-23T12:05:00Z", "open": 105, "high": 115, "low": 100, "close": 110},
            {"datetime": "2024-08-23T12:10:00Z", "open": 110, "high": 120, "low": 105, "close": 115},
            {"datetime": "2024-08-23T12:15:00Z", "open": 115, "high": 125, "low": 110, "close": 120}
        ],
        [
            {
                "datetime": "2024-08-23T12:00:00Z",
                "open": 100,
                "high": 115,
                "low": 90,
                "close": 110
            },
            {
                "datetime": "2024-08-23T12:10:00Z",
                "open": 110,
                "high": 125,
                "low": 105,
                "close": 120
            }
        ]
    )
])
async def test_aggregation_10m_positive(get_bar_service, test_input, expected):
    fakeAPI = get_bar_service.barclient
    fakeAPI.set_fake_data(test_input)
    ans = await get_bar_service.get_aggregated_bar(target_interval=10, symbol="DDD", end_date="2023-10-07", start_date="2023-10-05")
    print(ans)
    assert ans == expected

@pytest.mark.parametrize("test_input, expected", [
    (
        [
            {"datetime": "2024-08-23T12:00:00Z", "open": 100, "high": 110, "low": 90, "close": 105},
            {"datetime": "2024-08-23T12:05:00Z", "open": 105, "high": 115, "low": 100, "close": 110},
            {"datetime": "2024-08-23T12:10:00Z", "open": 110, "high": 120, "low": 105, "close": 115}
        ],
        [
            {
                "datetime": "2024-08-23T12:00:00Z",
                "open": 100,
                "high": 120,
                "low": 90,
                "close": 115
            }
        ]
    ),
    (
        [
            {"datetime": "2024-08-23T12:00:00Z", "open": 100, "high": 110, "low": 90, "close": 105},
            {"datetime": "2024-08-23T12:05:00Z", "open": 105, "high": 115, "low": 100, "close": 110},
            {"datetime": "2024-08-23T12:10:00Z", "open": 110, "high": 120, "low": 105, "close": 115},
            {"datetime": "2024-08-23T12:15:00Z", "open": 115, "high": 125, "low": 110, "close": 120},
            {"datetime": "2024-08-23T12:20:00Z", "open": 120, "high": 130, "low": 115, "close": 125},
            {"datetime": "2024-08-23T12:25:00Z", "open": 125, "high": 135, "low": 120, "close": 130}
        ],
        [
            {
                "datetime": "2024-08-23T12:00:00Z",
                "open": 100,
                "high": 120,
                "low": 90,
                "close": 115
            },
            {
                "datetime": "2024-08-23T12:15:00Z",
                "open": 115,
                "high": 135,
                "low": 110,
                "close": 130
            }
        ]
    )
])
async def test_aggregation_15m_positive(get_bar_service, test_input, expected):
    fakeAPI = get_bar_service.barclient
    fakeAPI.set_fake_data(test_input)
    ans = await get_bar_service.get_aggregated_bar(target_interval=15, symbol="DDD", end_date="2023-10-07", start_date="2023-10-05")
    assert ans == expected


async def test_invalid_interval_0(get_bar_service):
    with pytest.raises(InvalidTargetInterval) as exc_info:
        await get_bar_service.get_aggregated_bar(target_interval=-1, symbol="DDD", end_date="2023-10-07", start_date="2023-10-05")

    assert "target interval can not be lower than 0" in str(exc_info.value)


async def test_invalid_interval_5(get_bar_service):
    with pytest.raises(InvalidTargetInterval) as exc_info:
        await get_bar_service.get_aggregated_bar(target_interval=4, symbol="DDD", end_date="2023-10-07", start_date="2023-10-05")

    assert "target interval must be divisible by 5" in str(exc_info.value)



@pytest.mark.parametrize("test_input, target_interval", [
    (
        [{"datetime": "2024-08-23T12:00:00Z", "open": 100, "high": 110, "low": 90, "close": 105}],
        10
    ),
    (
        [
            {"datetime": "2024-08-23T12:00:00Z", "open": 100, "high": 110, "low": 90, "close": 105},
            {"datetime": "2024-08-23T12:05:00Z", "open": 105, "high": 115, "low": 100, "close": 110}
        ],
        15
    ),
])
async def test_aggregation_not_enough_data(get_bar_service, test_input, target_interval):
    fakeAPI = get_bar_service.barclient
    fakeAPI.set_fake_data(test_input)
    
    with pytest.raises(InvalidTargetInterval) as exc_info:
        await get_bar_service.get_aggregated_bar(
            symbol="DDD",
            end_date="2023-10-07",
            start_date="2023-10-05",
            target_interval=target_interval,
           
        )
    assert "not enougth info for chose interval" in str(exc_info.value)
