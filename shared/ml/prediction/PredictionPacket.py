
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PredictionPacket:

    date: datetime
    pctReturn:float
    closePrediction:float
    riskScore:int

    def toDict(self):
        #json can't serialize datetime objects, so convert them to isoformat strings
        d = asdict(self)
        d['date'] = self.date.isoformat()
        return d