import pytest   
from adaptors.stubs.fake_api import FakeUpshelAPI
from core.ports import bar_service
from adaptors.bar_service import BarServiceAdaptor

@pytest.fixture(scope="function")
def get_bar_service():
    api_adaptor = FakeUpshelAPI(
        endpoint_url="localhost:3002/crypto/data", auth_key="dsds"
    )
    return BarServiceAdaptor(barclient=api_adaptor)
