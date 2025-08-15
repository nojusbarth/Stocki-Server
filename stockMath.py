# copyright (c) Dr. Oliver Barth 2021

import math 
from scipy.signal import butter, lfilter

class StockMath():
    #
    def __init__(self):
        pass
    
    #
    def getMomentum(self, vals, diff):
        momentum = []
        for i in range(0, len(vals)):
            if i >= diff:
                momentum.append((vals[i] - vals[i - diff]) / vals[i - diff] * 100.0)
            else:
                momentum.append(0.0)
        return momentum
    
    #
    def getAverage(self, vals, n):
        average = []
        sum = 0
        for i in range(0, len(vals)):
            sum += vals[i]
            if i >= (n - 1):
                average.append(sum / n)
                sum -= vals[i - (n - 1)]
            else:
                average.append(vals[i])
        return average
    
    #
    def getMax(self, vals, n, fromBack = True):
        max = -1.0E9
        size = len(vals)
        for i in range(size - n, size):
            if vals[i] > max:
                max = vals[i]
        return max
    
    #
    def getMin(self, vals, n, fromBack = True):
        min = 1.0E9
        size = len(vals)
        for i in range(size - n, size):
            if vals[i] < min:
                min = vals[i]
        return min
    
    #
    def get_bandpass(self, lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    #
    def apply_bandpass_filter(self, data, lowcut, highcut, fs, order=3):
        b, a = self.get_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y
    
    #
    def getSqDist(self, p1, p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return (dx * dx + dy * dy)
    
    #
    def calcEigenSymmetric(self, mat, eigenVal, eigenVec0, eigenVec1):
        angToX = 0.0
        sig2Sq = mat[0][0]
        sig1Sq = mat[1][1]
        mu12 = mat[0][1]
    
        # calc eigenvalues
        root = math.sqrt(math.pow( (sig1Sq - sig2Sq) / 2.0, 2) + mu12 * mu12)
        sum = (sig1Sq + sig2Sq) / 2.0
        eigenVal[0] = sum + root
        eigenVal[1] = sum - root
    
        # calc eigenvectors
        if math.fabs(sig2Sq - eigenVal[0]) < 1E-6:
            angToX = math.pi / 2.0             
        else:
            dy = mu12 / (sig2Sq - eigenVal[0])
            angToX = math.atan2(dy, 1.0)
    
        # in direction of minimum covariance
        eigenVec1[0] = math.cos(angToX)
        eigenVec1[1] = math.sin(angToX)
    
        # in direction of maximum covariance
        eigenVec0[0] = -math.sin(angToX)
        eigenVec0[1] = math.cos(angToX)
        
    #
    def mulDot(self, v0, v1):
        val = v0[0] * v1[0] + v0[1] * v1[1]
        return val
        
