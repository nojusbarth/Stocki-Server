from dataclasses import dataclass


@dataclass
class ModelInfo:
    latestUpdate: str
    trainUntil: str
    metrics : dict
    features: list
    hyperParameters: dict
    numSamples : int
    trainTestSplit: float