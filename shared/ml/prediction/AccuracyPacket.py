
from dataclasses import dataclass


@dataclass
class AccuracyPacket:

    closePrediction:float
    pctReturnPrediction:float
    actualClose:float
    riskPrediction:int
