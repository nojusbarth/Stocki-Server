from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ModelInfo:
    latestUpdate: datetime
    trainUntil: datetime
    metrics : dict
    features: list
    hyperParameters: dict
    numSamples : int
    trainTestSplit: float

    def toDict(self):
        #json can't serialize datetime objects, so convert them to isoformat strings
        d = asdict(self)
        d['latestUpdate'] = self.latestUpdate.isoformat()
        d['trainUntil'] = self.trainUntil.isoformat()
        return d