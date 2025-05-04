from dataclasses import dataclass


@dataclass
class ServiceLayerException(Exception):
    message: str
