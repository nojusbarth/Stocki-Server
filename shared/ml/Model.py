
#simple wrapper to bond a model and a scaler together
class Model(object):
    
    def __init__(self, model, scaler):
        self.model = model
        self.scaler = scaler
        self.info = None


    def fit(self, Xdata, Ydata, **kwargs):
        Xscaled = self.scaler.fit_transform(Xdata)
        self.model.fit(Xscaled, Ydata, **kwargs)
        return self


    def predict(self, Xdata):
        Xscaled = self.scaler.transform(Xdata)
        return self.model.predict(Xscaled)

    def addInfo(self, info):
        self.info = info


    #getters just for file saving
    def getModel(self):
        return self.model

    def getScaler(self):
        return self.scaler

    def getInfo(self):
        return self.info