
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StockUpdateInfo:
    stockName : str
    latestUpdateTime : datetime
    interval : str