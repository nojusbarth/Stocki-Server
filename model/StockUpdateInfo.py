
from dataclasses import dataclass


@dataclass
class StockUpdateInfo:
    stockName : str
    latestUpdateTime : str