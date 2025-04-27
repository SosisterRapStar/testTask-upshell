from dataclasses import dataclass
from core.ports.bar_service import BarService
from adaptors.upshel_api import UpshelAPI
from adaptors.bar_service import BarServiceAdaptor
from config import config

@dataclass
class DIContainer:
    bar_service: BarService


def get_prod_container() -> DIContainer:
    api_adaptor = UpshelAPI(endpoint_url="localhost:3002/crypto/data", auth_key=config.BIT_API_KEY)
    return DIContainer(bar_service=BarServiceAdaptor(barclient=api_adaptor))
