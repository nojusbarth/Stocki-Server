
from dataclasses import dataclass
from datetime import date


@dataclass
class PredictionPacket:

    date: str
    pctReturn:float
    closePrediction:float
    riskScore:int