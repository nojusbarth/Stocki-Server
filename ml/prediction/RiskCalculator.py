#score between 0 and 100, where 0 is low risk and 100 is high risk, 10% error -> 100

class RiskCalculator:


    def calculateRisk(self, modelInfo, predicedPrice, futureStep, interval):

        maxRelError = 0.05 if interval == "1d" else 0.01 # 5% for daily, 1% for hourly

        rmse = modelInfo.metrics["RMSE"]
        mae = modelInfo.metrics["MAE"]
        r2 = modelInfo.metrics["R2"]

        errorGrowthFactor = futureStep ** 0.5  
        adjustedRmse = rmse * errorGrowthFactor
        adjustedMae = mae * errorGrowthFactor

        relRmse = adjustedRmse / predicedPrice
        relMae = adjustedMae / predicedPrice

        baseError = (relRmse + relMae) / 2

        score = baseError * 100 / maxRelError
        score = min(score, 100)

        r2Factor = 1 + max(0, 1 - r2)
        score *= r2Factor
        score = min(score, 100)

        return int(score)

