from dataclasses import dataclass


@dataclass
class ServiceLayerException(Exception):
    code: str
    message: str
