
from dataclasses import dataclass
from datetime import date


@dataclass
class AccuracyPacket:

    closePrediction:float
    pctReturnPrediction:float
    actualClose:float
    riskPrediction:int
