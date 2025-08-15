# Copyright (c) 2021 Dr. Oliver Barth

import tkinter as tk
from tkinter import ttk
from drbLayout import *

#
class PlotXY():
    
    #
    def __init__(self, frm, active):
        self.frm = frm
        self.active = active

    #
    def setup(self, borderYPercent, addYAxis, nXTicks, nYTicks, lineColors, plotType, drawZero, width=700, height=400):
        self.numXTicks = nXTicks
        self.numYTicks = nYTicks
        self.deletePlot = False
        self.redrawTicks = False
        self.borderYPercent = borderYPercent
        self.w = width
        self.h = height
        self.hBorder = [0, 0, 0, 0]
        self.wYAxis = 40
        self.canvYAxis = []
        for i in range(0, 4):
            self.hBorder[i] = height * borderYPercent[i]  
            cvs = tk.Canvas(self.frm, background='lightgrey',  width=self.wYAxis, height=self.h)
            cvs.grid(column=i, row=0, rowspan=10, sticky='nsew')
            self.canvYAxis.append(cvs)
        self.canv = tk.Canvas(self.frm, background='lightgrey', width=self.w, height=self.h)
        self.canv.grid(column=4, row=0, rowspan=10, columnspan=5, sticky='nsew')
        self.canvXAxis = tk.Canvas(self.frm, background='lightgrey',  width=self.w, height=self.wYAxis)
        self.canvXAxis.grid(column=4, row=11, columnspan=5, sticky='nsew')
        self.yMax = [ -1E9, -1E9, -1E9, -1E9 ]
        self.yMin = [ 1E9, 1E9, 1E9, 1E9 ]
        self.xAct = 0
        self.xActLabels = []
        self.xValues = []
        self.yValues = [[], [], [] ,[]]
        self.lines = []
        self.selChannel = ['', '', '', '']
        self.lineCols = lineColors
        self.addYAxis = addYAxis
        self.plotType = plotType
        self.drawZero = drawZero

    #
    def setActive(self, active):
        self.active = active

    
    #
    def setXMax(self, xmax):
        self.xMax = xmax
    
    #
    def changeXMax(self):
        self.xMax = float(self.entryMaxX.get())
        if self.xMax <= 0.0:
            self.xMax = 1.0

    # append 1 point to each line self.yValues[0 .. 3]
    def addPoints(self, pnts, lbl):
        self.xValues.append(self.xAct)
        self.xActLabels.append(lbl)
        for i in range (0, len(pnts)):
            if pnts[i] > self.yMax[i]:
                self.yMax[i] = pnts[i]
                self.redrawTicks = True
            if pnts[i] < self.yMin[i]:
                self.yMin[i] = pnts[i]
                self.redrawTicks = True
        for i in range (0, 4):
            self.yValues[i].append(pnts[i])
        self.xAct += 1
            
    #
    def addLine(self, line):
        self.lines.append(line)
    
    # 
    def __trafoXToScreen(self, x):
        x = (x * self.w) / self.xMax
        xint = int(round(x))
        return xint

    # 
    def __trafoYToScreen(self, y, n):
        yMax = self.yMax[n]
        yMin = self.yMin[n]
        
        for i in range(1, 4):
            if self.active[i] and self.addYAxis[i] == False:
                if self.yMax[i] > yMax:
                    yMax = self.yMax[i]
                if self.yMin[i] < yMin:
                    yMin = self.yMin[i]       
        y -= yMin
        den = yMax - yMin
        if den != 0:
            y *= (self.h - 2.0 * self.hBorder[n]) / den
        else:
            y = 0
        y = self.h - self.hBorder[n] - y
        yint = round(y)
        return yint
    
    #
    def redraw(self):
        # draw self.xValues[], self.yValues[][]
        for i in range(0, 4):
            if not self.active[i]:
                continue
            col = self.lineCols[i]
            datalen = len(self.xValues)
            for k in range(0, datalen):
                if k <= datalen - 2:
                    x0data = self.xValues[k]
                    x1data = self.xValues[k + 1]
                    y0data = self.yValues[i][k]
                    y1data = self.yValues[i][k + 1]
                    x0 = self.__trafoXToScreen(x0data)
                    x1 = self.__trafoXToScreen(x1data)
                    if self.addYAxis[i]: 
                        y0 = self.__trafoYToScreen(y0data, i)
                        y1 = self.__trafoYToScreen(y1data, i)
                    else:
                        y0 = self.__trafoYToScreen(y0data, i - 1)
                        y1 = self.__trafoYToScreen(y1data, i - 1)
                    if self.plotType[i] == 'line':
                        self.canv.create_line(x0, y0, x1, y1, fill=col)
                        # print data point number
                        #tickLbl = str(datalen - k - 2) + ":" + "{:.2f}".format(y1data) 
                        #t = self.canv.create_text(x1, y1-5, text=tickLbl, font='Arial, 7')
                    elif self.plotType[i] == 'circle':
                        self.canv.create_oval(x1 - 1, y1 - 1, x1 + 1, y1 + 1, activeoutline=col, fill=col)
                if self.drawZero[i]:
                    start = self.__trafoXToScreen(self.xValues[0])
                    end = self.__trafoXToScreen(self.xValues[-1])
                    self.canv.create_line(start, self.__trafoYToScreen(0, i), end, self.__trafoYToScreen(0, i), dash=(2, 4), fill='blue')
                        
        for i in range(0, len(self.lines)):
            l = self.lines[i]
            x0 = self.__trafoXToScreen(l[0][0])
            y0 = self.__trafoYToScreen(l[0][1], 0)
            x1 = self.__trafoXToScreen(l[1][0])
            y1 = self.__trafoYToScreen(l[1][1], 0)
            self.canv.create_line(x0, y0, x1, y1, fill='black')            
        
        if self.redrawTicks:
            # draw x-ticks
            self.canvXAxis.delete("all")
            xStep = self.xMax / self.numXTicks
            xTick = 0
            #actLabel = 0
            for i in range (0, self.numXTicks):
                # draw ticks in canvas x axis
                x0 = self.__trafoXToScreen(xTick)
                x1 = x0
                y0 = 0
                y1 = 10
                l = self.canvXAxis.create_line(x0, y0, x1, y1, fill='black')
                tickLbl = self.xActLabels[int(xTick)]
                t = self.canvXAxis.create_text(x0+12, y1+8, text=tickLbl, font='Arial, 7')
                xTick += xStep
                #actLabel += 1
            #draw y-ticks
            for i in range (0, 4):
                if not self.active[i]:
                    continue
                self.canvYAxis[i].delete("all")
                if self.addYAxis[i]:    
                    yStep = (self.yMax[i] - self.yMin[i]) / self.numYTicks[i]
                    yTick = self.yMin[i]
                    for k in range (0, self.numYTicks[i] + 1):
                        # draw ticks in canvas y axis
                        x0 = self.wYAxis
                        x1 = self.wYAxis - 10
                        y0 = self.__trafoYToScreen(yTick, i)
                        y1 = y0
                        l = self.canvYAxis[i].create_line(x0, y0, x1, y1, fill='black')
                        tickLbl = "{:.2f}".format(yTick) 
                        t = self.canvYAxis[i].create_text(x1-8, y1-5, text=tickLbl, font='Arial, 7')
                        
                        # draw horizontal lines in canvas
                        if i == 0:
                            x0 = 0
                            x1 = self.w
                            y0 = self.__trafoYToScreen(yTick, i)
                            y1 = y0
                            l = self.canv.create_line(x0, y0, x1, y1, dash=(2, 4), fill='white')
                        yTick += yStep
            self.redrawTicks = False
