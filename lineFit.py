# copyright (c) Dr. Oliver Barth 2021


from stockMath import *
import copy

LINEFIT_DEBUG_ON = False 

class LineFit():
	#
	def __init__(self):
		self.tol = 1e-4 * 1000
		self.minSegLen = 5.0
		self.maxSegLen = 1000.0
		self.maxDistInSeg = 20.0
		self.minPntInSeg = 20
		self.maxSqSegLen = self.maxSegLen * self.maxSegLen
		self.minSqSegLen = self.minSegLen * self.minSegLen
		self.maxSqDistInSeg = self.maxDistInSeg * self.maxDistInSeg
		self.minSqSegLen = 0
		self.sum_n = 0.0
		self.sum_sx = 0.0
		self.sum_sy = 0.0
		self.sum_sxx = 0.0
		self.sum_syy = 0.0
		self.sum_sxy = 0.0
		self.firstPntOfSeg = 0
		self.numFirstPnt = 0
		self.lastPntOfSeg = 0
		self.numLastPnt = 0
		self.vecPnt = []
		self.math = StockMath()
		self.yScale = 1.0

	#
	def initPoint(self, pnt, n):
		self.sum_n = 1.0
		self.sum_sx = pnt[0]
		self.sum_sy = pnt[1]
		self.sum_sxx = pnt[0] * pnt[0]
		self.sum_syy = pnt[1] * pnt[1]
		self.sum_sxy = pnt[0] * pnt[1]
		self.firstPntOfSeg = pnt
		self.numFirstPnt = n
		self.lastPntOfSeg = pnt
		self.numLastPnt = n
		
	#
	def addPoint(self, pnt, n):
		self.sum_n += 1
		self.sum_sx += pnt[0]
		self.sum_sy += pnt[1]
		self.sum_sxx += pnt[0] * pnt[0]
		self.sum_syy += pnt[1] * pnt[1]
		self.sum_sxy += pnt[0] * pnt[1]
		self.lastPntOfSeg = pnt
		self.numLastPnt = n
		
	#
	def removePoint(self, pnt, prevpnt, n):
		self.sum_n -= 1
		self.sum_sx -= pnt[0]
		self.sum_sy -= pnt[1]
		self.sum_sxx -= pnt[0] * pnt[0]
		self.sum_syy -= pnt[1] * pnt[1]
		self.sum_sxy -= pnt[0] * pnt[1]
		self.lastPntOfSeg = prevpnt
		self.numLastPnt = n - 1

	#
	def fit(self, values, covOrth):
		vecLineSeg = []
		if len(values) < 2:
			return vecLineSeg
		
		# find min, max
		self.vecPnt = []
		pnt = [0.0, 0.0]
		min = 1.0E9
		max = 1.0E-9
		nvalues = len(values)
		for i in range(0, nvalues):
			pnt = [i, values[i]]
			#pnt = [i, i % 20]
			self.vecPnt.append(pnt)
			if values[i] > max:
				max = values[i]
			if values[i] < min:
				min = values[i]
		
		# scale y values
		self.vecPntScaled = []
		self.yScale = nvalues / (max - min)
		min = 1.0E9
		max = 1.0E-9
		for i in range(0, nvalues):
			pnt = [i, values[i] * self.yScale]
			#pnt = [i, i % 20]
			self.vecPntScaled.append(pnt)
			if (values[i] * self.yScale) > max:
				max = values[i] * self.yScale
			if (values[i] * self.yScale) < min:
				min = values[i] * self.yScale
		maxCovOrth = (max - min) * covOrth / 100.0
			
		# init first point
		self.initPoint(self.vecPntScaled[0], 0)
		
		# fit lines
		for i in range (1, len(self.vecPntScaled)):
			self.addPoint(self.vecPntScaled[i], i)
			
			# next point not valid for current line seg?
			distLastToAct =  self.math.getSqDist(self.vecPntScaled[i - 1], self.vecPntScaled[i])
			distFirstToLast = self.math.getSqDist(self.firstPntOfSeg, self.lastPntOfSeg)
			if 	(distLastToAct > self.maxSqDistInSeg) or (distFirstToLast > self.maxSqSegLen):
				# not valid, try to finish current segment
				seg = [[0.0, 0.0], [0.0, 0.0]]
				if self.finishLineSeg(seg):
					# rescale y values only
					seg[0][1] /= self.yScale
					seg[1][1] /= self.yScale
					vecLineSeg.append(seg)
	
				# start new segment
				self.initPoint(self.vecPntScaled[i], i)
			#if self.sum_sx != self.sum_sy:
			#	print ("s")
			isValid = self.isValidLineSeg(maxCovOrth)
			if not isValid:
				self.removePoint(self.vecPntScaled[i], self.vecPntScaled[i - 1], i)
				seg = [[0.0, 0.0], [0.0, 0.0]]
				if self.finishLineSeg(seg):
					seg[0][1] /= self.yScale
					seg[1][1] /= self.yScale
					vecLineSeg.append(seg)
	
				# start new segment
				self.initPoint(self.vecPntScaled[i], i)
		seg = [[0.0, 0.0], [0.0, 0.0]]
		if self.finishLineSeg(seg):
			seg[0][1] /= self.yScale
			seg[1][1] /= self.yScale
			vecLineSeg.append(seg)
		
		return vecLineSeg
	
	#
	def isValidLineSeg(self, maxCovOrth):
		if self.sum_n <= 1:
			return True
		
		# calculate mean point
		vecMean = [0.0, 0.0]
		vecMean[0] = self.sum_sx / self.sum_n
		vecMean[1] = self.sum_sy / self.sum_n
	
		# calculate covariance
		cov = [[0.0, 0.0], [0.0, 0.0]]
		cov[0][0] = self.sum_sxx / self.sum_n - vecMean[0] * vecMean[0]
		cov[1][1] = self.sum_syy / self.sum_n - vecMean[1] * vecMean[1]
		cov[0][1] = self.sum_sxy / self.sum_n - vecMean[0] * vecMean[1]
		cov[1][0] = cov[0][1]
	
		# calculate eigenvalues / eigenVectors
		eigenVal = [0.0, 0.0]
		eigenVec0 = [0.0, 0.0]
		eigenVec1 = [0.0, 0.0]
		self.math.calcEigenSymmetric(cov, eigenVal, eigenVec0, eigenVec1)
	
		if (math.fabs(eigenVal[0] - eigenVal[1]) < self.tol):
			return False;
	
		covOrth = 0.0
		if eigenVal[0] < eigenVal[1]:
			covOrth = eigenVal[0]
		else:
			covOrth = eigenVal[1]
	
		if covOrth > maxCovOrth:
			return False
	
		return True

	#
	def finishLineSeg(self, line):
		if self.sum_n < self.minPntInSeg:
			return False
		
		# calculate mean point
		vecMean = [0.0, 0.0]
		vecMean[0] = self.sum_sx / self.sum_n
		vecMean[1] = self.sum_sy / self.sum_n
	
		# calculate covariance
		cov = [[0.0, 0.0], [0.0, 0.0]]
		cov[0][0] = self.sum_sxx / self.sum_n - vecMean[0] * vecMean[0]
		cov[1][1] = self.sum_syy / self.sum_n - vecMean[1] * vecMean[1]
		cov[0][1] = self.sum_sxy / self.sum_n - vecMean[0] * vecMean[1]
		cov[1][0] = cov[0][1]
	
		# calculate eigenvalues / eigenVectors
		eigenVal = [0.0, 0.0]
		eigenVec0 = [0.0, 0.0]
		eigenVec1 = [0.0, 0.0]
		self.math.calcEigenSymmetric(cov, eigenVal, eigenVec0, eigenVec1)
	
		eigenVec = [0.0, 0.0]
		if eigenVal[0] < eigenVal[1]:
			eigenVec[0] = eigenVec1[0]
			eigenVec[1] = eigenVec1[1]
		else:
			eigenVec[0] = eigenVec0[0]
			eigenVec[1] = eigenVec0[1]
	
		# 
		meanToFirst = [0.0, 0.0]
		meanToFirst[0] = self.firstPntOfSeg[0] - vecMean[0]
		meanToFirst[1] = self.firstPntOfSeg[1] - vecMean[1]
		if self.math.mulDot(meanToFirst, eigenVec) > 0.0:
			eigenVec[0] = -eigenVec[0]
			eigenVec[1] = -eigenVec[1]
		mulLen1 = self.math.mulDot(meanToFirst, eigenVec)
		line[0][0] = vecMean[0] + mulLen1 * eigenVec[0]
		line[0][1] = vecMean[1] + mulLen1 * eigenVec[1]
		if line[0][0] < 0.0:
			line[0][0] = 0.0
				
		#
		meanToLast = [0.0, 0.0]
		meanToLast[0] = self.lastPntOfSeg[0] - vecMean[0] 
		meanToLast[1] = self.lastPntOfSeg[1] - vecMean[1] 
		mulLen2 = self.math.mulDot(meanToLast, eigenVec)
		line[1][0] = vecMean[0] + mulLen2 * eigenVec[0]
		line[1][1] = vecMean[1] + mulLen2 * eigenVec[1]
		if line[1][0] < 0.0:
			line[1][0] = 0.0	

		if self.math.getSqDist(line[0], line[1]) < self.minSqSegLen:
			return False
	
		# debug
		if LINEFIT_DEBUG_ON:
			print ('--------------------')
			print ('1:' + str(self.firstPntOfSeg) + ' 2:' + str(self.lastPntOfSeg))
			print ('cov:' + str(cov) + ' evec:' + str(eigenVec))
			print ('mean:' + str(vecMean))
			print ('mtof:' + str(meanToFirst) + ' mtol:' + str(meanToLast))
			print ('mul1:' + str(mulLen1) + ' mul2:' + str(mulLen2))
			print ('line:' + str(line))
		
		return True
