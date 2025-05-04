import dotenv
import logging
from dataclasses import dataclass
import os

dotenv.load_dotenv()


logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)


@dataclass
class Config:
    BIT_API_KEY: str = "dIO2nxsWxK2j2w84cKz"


config = Config()
