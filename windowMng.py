# copyright (c) Dr. Oliver Barth 2021

import threading
import tkinter as tk
from tkinter import ttk
from datetime import date
from scipy.fftpack import fft
import scipy.signal as signal
import numpy as np
from yahoofinancials import YahooFinancials
from matplotlib.ticker import MaxNLocator
from stockMath import *
from stockList import *
from plotXY import *
from lineFit import *
import copy
import json


#NEW 
import pandas as pd
#

from idlelib.tooltip import Hovertip


STOCKI_TIME_INTERVAL = OrderedDict([
    ('1 week', '5'),
    ('1 month', '20'),
    ('3 month', '60'),
    ('6 month', '120'),
    ('1 year', '240'),
    ('2 year', '480'),
    ('3 year', '720'),
    ('max', '')
    ])


STOCKI_RUN_TEST = False
STOCKI_READ_DIVIDEND = True
STOCKI_FRAME_MAIN_SHOW = ['open_close_high_low', 'open_close_average']
STOCKI_N_AVERAGE = ['7', '20', '100', '200']
STOCKI_N_MOMENTUM = ['5', '10', '20', '50']
STOCKI_LAYOUT_frameGeometry = '1400x1000'
STOCKI_LAYOUT_AppTitle = 'drb STOCKI - v0.0.1'
STOCKI_LAYOUT_font = 'Calibri 8'
STOCKI_LINEWIDTH = 0.5
STOCKI_COV = '14'


#
class WindowMng():
    #
    def __init__(self, root):
        
        self.stockMath = StockMath()
        
        self.loadFav()
        
        # get pricedata
        self.stock_dict = OrderedDict()
        if STOCKI_RUN_TEST:
            self.stock_dict = STOCKI_STOCKNAMES_TEST
        else:
            self.stock_dict = STOCKI_STOCKNAMES

        
       
        self.yahoo_financials = YahooFinancials(list(self.stock_dict.values()))
        today = date.today()
        enddate = today.strftime("%Y-%m-%d")
        print("try reading historical price data")
        self.pricedata = self.yahoo_financials.get_historical_price_data(start_date=enddate, 
                                                      end_date=enddate, 
                                                      time_interval='daily')
        
        
        ##new
        #
        #path = r'E:\\Prog\\Python\\Stocki\\financedata\\'
        #
        #symbols = list(self.stock_dict.values())
        #
        #for symbol in symbols:
        #    prices = self.pricedata[symbol]['prices']
        #    df = pd.DataFrame(prices)
        #    df.to_csv(path + symbol + '.csv',index=False)
        #
        #    print('Data written: ' + symbol)
        #
        #
        #

        x = threading.Thread(target=self.updateToday, args=(1,))
        x.start()

        frameNav = ttk.Frame(root, padding=5)
        frameNav.grid(column=0, row=0, sticky="ew")
        
        self.framePrices = ttk.Frame(root, padding=5)
        self.framePrices.grid(column=0, row=1, sticky="ew")
        
        self.frameInfo = ttk.Frame(root, padding=5)
        self.frameInfo.grid(column=0, row=2, sticky="ew")
        
        self.frameAnalytics = ttk.Frame(root, padding=5)
        self.frameAnalytics.grid(column=1, row=1, sticky="ew")
        
        self.frameFFT = ttk.Frame(root, padding=5)
        self.frameFFT.grid(column=1, row=2, sticky="ew")
        
        self.comboStockname = ttk.Combobox(frameNav, values=list(self.stock_dict.keys()), width=50, font=STOCKI_LAYOUT_font)
        self.comboStockname.grid(column=0, row=0, columnspan=2, sticky="ns", padx=2, pady=2)
        self.comboStockname.current(0)
        self.comboStockname.bind("<<ComboboxSelected>>", self.drawStockSelected)
        
        stock_key = self.comboStockname.get()
        stock_name = self.stock_dict[stock_key]
        self.maxDays = len(self.pricedata[stock_name]['prices'])
        
        self.butShowPrev = ttk.Button(frameNav, text='<', width=10, command=self.showPrev)
        self.butShowPrev.grid(column=0, row=1, sticky="ew", padx=5, pady=5)
        self.butShowNext = ttk.Button(frameNav, text='>', width=10, command=self.showNext)
        self.butShowNext.grid(column=1, row=1, sticky="ew", padx=5, pady=5)
        
        self.comboTimeInterval = ttk.Combobox(frameNav, width=25, font=STOCKI_LAYOUT_font)
        self.comboTimeInterval['values'] = list(STOCKI_TIME_INTERVAL.keys())
        self.comboTimeInterval.grid(column=0, row=2, columnspan=1, sticky="ns", padx=2, pady=2)
        self.comboTimeInterval.current(3)
        self.comboTimeInterval.bind("<<ComboboxSelected>>", self.drawStockSelected)
        toolTip = Hovertip(self.comboTimeInterval,'time interval')
        
        self.addInfo = tk.StringVar()
        self.labelAddInfo = ttk.Label(frameNav, width=25, textvariable=self.addInfo, font=STOCKI_LAYOUT_font)
        self.labelAddInfo.grid(column=1, row=2, columnspan=1, sticky="ns", padx=2, pady=2)
        
        self.comboNAverage = ttk.Combobox(frameNav, width=20, values=STOCKI_N_AVERAGE, font=STOCKI_LAYOUT_font)
        self.comboNAverage.grid(column=4, row=0, columnspan=2, sticky="ns", padx=2, pady=2)
        self.comboNAverage.current(3)
        self.comboNAverage.bind("<<ComboboxSelected>>", self.drawStockSelected)
        toolTip = Hovertip(self.comboNAverage,'number average')
        
        self.comboFrameMainShow = ttk.Combobox(frameNav, width=20, values=STOCKI_FRAME_MAIN_SHOW, font=STOCKI_LAYOUT_font)
        self.comboFrameMainShow.grid(column=4, row=1, columnspan=2, sticky="ns", padx=2, pady=2)
        self.comboFrameMainShow.current(0)
        self.comboFrameMainShow.bind("<<ComboboxSelected>>", self.drawStockSelected)
        
        self.spin_current_value = tk.StringVar()
        self.spin_current_value.set("20")
        self.spin_momentum = ttk.Spinbox( frameNav, width=20, from_=10, to=60, textvariable=self.spin_current_value, wrap=True,
                                          command= lambda: self.drawStockSelected(None), font=STOCKI_LAYOUT_font)
        self.spin_momentum.grid(column=4, row=2, columnspan=2, sticky="ns", padx=2, pady=2)
        toolTip = Hovertip(self.spin_momentum,'momentum')
            
        self.bandpass_low_value = tk.StringVar()
        self.bandpass_low_value.set("4")
        self.bandpass_low = ttk.Spinbox( frameNav, width=20, from_=1, to=499, increment=1, textvariable=self.bandpass_low_value, wrap=True,
                                         command= lambda: self.drawStockSelected(None), font=STOCKI_LAYOUT_font)
        self.bandpass_low.grid(column=6, row=0, columnspan=2, sticky="ns", padx=2, pady=2)
        toolTip = Hovertip(self.bandpass_low,'bandpass low')
            
        self.bandpass_high_value = tk.StringVar()
        self.bandpass_high_value.set("60")
        self.bandpass_high = ttk.Spinbox( frameNav, width=20, from_=1, to=500, increment=1, textvariable=self.bandpass_high_value, wrap=True,
                                          command= lambda: self.drawStockSelected(None), font=STOCKI_LAYOUT_font)
        self.bandpass_high.grid(column=6, row=1, columnspan=2, sticky="ns", padx=2, pady=2)
        toolTip = Hovertip(self.bandpass_high,'bandpass high')
            
        self.covorth_value = tk.StringVar()
        self.covorth_value.set(STOCKI_COV)
        self.covorth = ttk.Spinbox( frameNav, width=20, from_=1, to=80, increment=1, textvariable=self.covorth_value, wrap=True,
                                    command= lambda: self.drawStockSelected(None), font=STOCKI_LAYOUT_font)
        self.covorth.grid(column=8, row=0, columnspan=2, sticky="ns", padx=2, pady=2)
        toolTip = Hovertip(self.covorth,'covariance')
        
        self.butPrintData = ttk.Button(frameNav, text='print', width=10, command=self.printData)
        self.butPrintData.grid(column=10, row=0, sticky="ew", padx=5, pady=5)
        
        self.loadFav = ttk.Button(frameNav, text='load', width=10, command=self.loadFav)
        self.loadFav.grid(column=11, row=0, sticky="ew", padx=5, pady=5)
        
        self.saveFav = ttk.Button(frameNav, text='save', width=10, command=self.saveFav)
        self.saveFav.grid(column=11, row=1, sticky="ew", padx=5, pady=5)
        
        self.toggleFav = ttk.Button(frameNav, text='show fav', width=10, command=self.toggleFav)
        self.toggleFav.grid(column=11, row=2, sticky="ew", padx=5, pady=5)
        
        self.addFav = ttk.Button(frameNav, text='add fav', width=10, command=self.addFav)
        self.addFav.grid(column=12, row=0, sticky="ew", padx=5, pady=5)
        
        self.delFav = ttk.Button(frameNav, text='del fav', width=10, command=self.delFav)
        self.delFav.grid(column=12, row=1, sticky="ew", padx=5, pady=5)
        
        self.lineFit = LineFit()
        
        self.drawStockSelected(None)
        
    #
    def updateToday(self, name):
        print('try reading price data')
        #self.stockpricedata = self.yahoo_financials.get_stock_price_data()
        print('try reading summary data')
        #stocksummarydata = self.yahoo_financials.get_stock_tech_data('summaryDetail')
        #print('ready')
        
        stocknames = list(self.stock_dict.values())
        stocknames_long = list(self.stock_dict.keys())
        i = -1
        for st in stocknames:
            i += 1
            if (i < 22) or (stocknames_long[i] == 'Deutsche Telekom AG'):
                continue
                      
            print('update:' + stocknames_long[i])
            
            try:
                stockpricedata = YahooFinancials(st).get_stock_price_data()
                
                prices_end = copy.deepcopy(self.pricedata[st]['prices'][-1])
                prices_end['open'] = stockpricedata[st]['regularMarketOpen']
                prices_end['close'] = stockpricedata[st]['regularMarketPrice']
                prices_end['high'] = stockpricedata[st]['regularMarketDayHigh']
                prices_end['low'] = stockpricedata[st]['regularMarketDayLow']
                prices_end['formatted_date'] = stockpricedata[st]['regularMarketTime']
                prices_end['volume'] = stockpricedata[st]['regularMarketVolume']
                
                marketCap = stockpricedata[st]['marketCap']
                if marketCap == None:
                    mcap = 0
                else:
                    mcap = marketCap
                prices_end['marketCap'] = mcap
                
                if prices_end['adjclose'] != None:
                    self.pricedata[st]['prices'].append(prices_end)
                
                currency = stockpricedata[st]['currency']
                prices_end['currency'] = currency                

                divRate = 0.0
                if STOCKI_READ_DIVIDEND:
                    stocksummarydata = YahooFinancials(st).get_stock_tech_data('summaryDetail')
                    divRate = stocksummarydata[st]['dividendRate']
                prices_end['dividendRate'] = divRate
                    
                #print(prices_end)
                #print(act_stock_price_data[st])
                #print('market cap:' + str(mcap / 1.0E6) + ' divident rate:' + str(divRate))
               
            except Exception as ex:
                print("ex:" + repr(ex))

    #
    def loadFav(self):
        global STOCKI_STOCKNAMES_FAV
        with open('stocki_fav.json', 'r') as read_file:
            STOCKI_STOCKNAMES_FAV = json.loads(read_file.read())
            self.stock_dict = STOCKI_STOCKNAMES_FAV

    #
    def saveFav(self):
        with open('stocki_fav.json', 'w') as f:
            ret = json.dumps(STOCKI_STOCKNAMES_FAV)
            f.write(ret)
    
    #
    def addFav(self):
        global STOCKI_STOCKNAMES_FAV
        stock_key = self.comboStockname.get()
        stock_name = self.stock_dict[stock_key]
        new = {stock_key : stock_name}
        STOCKI_STOCKNAMES_FAV.update(new)
    
    #
    def delFav(self):
        pass
    
    #
    def toggleFav(self):
        global STOCKI_STOCKNAMES_FAV
        txt = self.toggleFav['text']
        if txt == "show norm":
            self.toggleFav.config(text="show fav")
            self.comboStockname.delete(0, tk.END)
            self.stock_dict = STOCKI_STOCKNAMES_FAV
        else:
            self.toggleFav.config(text="show norm")
            self.comboStockname.delete(0, tk.END)
            if STOCKI_RUN_TEST:
                self.stock_dict = STOCKI_STOCKNAMES_TEST
            else:
                self.stock_dict = STOCKI_STOCKNAMES
        self.comboStockname["values"] = list(self.stock_dict.keys())
        self.comboStockname.current(0)
    
    #
    def showNext(self):
        newidx = self.comboStockname.current() + 1
        if newidx >= len(self.stock_dict):
            newidx = 0
        self.comboStockname.current(newidx)
        self.drawStockSelected(None)
        
    #
    def showPrev(self):
        newidx = self.comboStockname.current() - 1
        if newidx < 0:
            newidx = len(self.stock_dict) - 1
        self.comboStockname.current(newidx)
        self.drawStockSelected(None)
    
    #
    def printData(self):
        stock_key = self.comboStockname.get()
        stock_name = self.stock_dict[stock_key]
        stockprices = self.pricedata[stock_name]['prices']
        datalen = len(stockprices)
        for i in range(0, datalen):
            try:
                print(str(i) + ' ' + str(datalen - i - 1) + ' open:' + ("%.2f" % stockprices[i]['open']) + ' close:' +  ("%.2f" % stockprices[i]['close']) + ' high:' + ("%.2f" % stockprices[i]['high']) + ' low:' + ("%.2f" % stockprices[i]['low'])
                      + ' vol:' + ("%.2f" % stockprices[i]['volume']) + ' date:' + stockprices[i]['formatted_date'])
            except:
                print(str(i) + ' except')
                
    #
    def getDataList(self, stockname, dataname1, dataname2):
        stockprices = self.pricedata[stockname]['prices']
        dlist1 = []
        dlist2 = []
        for i in range(0, len(stockprices)):
            if stockprices[i][dataname1] != None:
                dlist1.append(stockprices[i][dataname1])
                if dataname2 != '':
                    dlist2.append(stockprices[i][dataname2])
        return dlist1, dlist2
    
    #
    def getStockprice(self, stock_name, ndays):
        stockprices = self.pricedata[stock_name]['prices']
        stpriceclose, stdates = self.getDataList(stock_name, 'close', 'formatted_date')
        n = len(stpriceclose) - ndays
        return  stpriceclose[n:]
    
    #
    # returns stock price data for the last ndays
    #
    def getStockdata(self, stock_name, ndays, nmomentum, naverage):
        stpriceopen, stdates = self.getDataList(stock_name, 'open', 'formatted_date')
        stpriceclose, stdates = self.getDataList(stock_name, 'close', 'formatted_date')
        stpriceadjclose, stdates = self.getDataList(stock_name, 'adjclose', 'formatted_date') # not used
        stpricehigh, stdates = self.getDataList(stock_name, 'high', 'formatted_date')
        stpricelow, stdates = self.getDataList(stock_name, 'low', 'formatted_date')
        volume, stdates = self.getDataList(stock_name, 'volume', 'formatted_date')
        
        momentum = self.stockMath.getMomentum(stpriceclose, int(nmomentum))
        average =  self.stockMath.getAverage(stpriceclose, int(naverage))
        
        n = len(stpriceopen) - ndays
        return  stpriceopen[n:], stpriceclose[n:], stpricehigh[n:], stpricelow[n:], stdates[n:], momentum[n:], average[n:], volume[n:]
    
    #
    def drawStockSelected(self, event):
        for widget in self.framePrices.winfo_children():
            widget.destroy()
            
        for widget in self.frameInfo.winfo_children():
            widget.destroy()
            
        for widget in self.frameAnalytics.winfo_children():
            widget.destroy()
            
        for widget in self.frameFFT.winfo_children():
            widget.destroy()
            
        # plot prices
        active = [True, True, True, True]
        plotPrices = PlotXY(self.framePrices, active)
        borderSize = [ 0.1, 0.1, 0.1, 0.1 ]
        addYAxis = [ True, False, False, False]
        nXTicks = 10
        nYTicks = [ 10, 10, 10, 10 ]
        lineColors = ['red', 'green', 'light coral', 'pale green']
        plotType = [ 'line', 'line', 'circle', 'circle' ]
        drawZero = [ False, False, False, False ]
        plotPrices.setup(borderSize, addYAxis, nXTicks, nYTicks, lineColors, plotType, drawZero)
        
        stock_key = self.comboStockname.get()
        stock_name = self.stock_dict[stock_key]
        time_interval_key = self.comboTimeInterval.get()
        if time_interval_key == 'max':
            ndays = 1000
        else:
            ndays = int(STOCKI_TIME_INTERVAL[time_interval_key])
            
        nmomentum = self.spin_momentum.get()
        naverage = self.comboNAverage.get()
        stprices_open, stprices_close, stprices_high, stprices_low, stdates, momentum, average, volume = self.getStockdata(stock_name, ndays, nmomentum, naverage)
        
        showType = self.comboFrameMainShow.get()
        plotPrices.setXMax(len(stprices_open))
        for i in range (0, len(stprices_open)):
            if showType == 'open_close_high_low':
                plotPrices.setActive([True, True, True, True])
                pnt = [stprices_open[i], stprices_close[i], stprices_high[i], stprices_low[i]]
            elif showType == 'open_close_average':
                plotPrices.setActive([True, True, True, False])
                pnt = [stprices_open[i], stprices_close[i], average[i], 0.0]
            else:
                pnt = [stprices_open[i], stprices_close[i], stprices_high[i], stprices_low[i]]
            plotPrices.addPoints(pnt, stdates[i])
        
        plotPrices.redraw()
        
        # plot momentum and volume
        active = [True, True, False, False]
        plotInfo = PlotXY(self.frameInfo, active)
        borderSize = [ 0.3, 0.1, 0.1, 0.1 ]
        addYAxis = [ True, True, False, False]
        nXTicks = 10
        nYTicks = [ 10, 10, 10, 10 ]
        lineColors = ['blue', 'grey', 'black', 'black']
        plotType = [ 'line', 'line', 'line', 'line' ]
        drawZero = [ True, False, False, False ]
        plotInfo.setup(borderSize, addYAxis, nXTicks, nYTicks, lineColors, plotType, drawZero)
        
        plotInfo.setXMax(len(stprices_open))
        for i in range (0, len(stprices_open)):
            pnt = [momentum[i], volume[i] / 1000000.0, 0.0, 0.0]
            plotInfo.addPoints(pnt, stdates[i])
        
        plotInfo.redraw()
        
        # plot line fitting and prices bandgap filtered
        active = [True, True, False, False]
        plotAnalytics = PlotXY(self.frameAnalytics, active)
        borderSize = [ 0.1, 0.3, 0.1, 0.1 ]
        addYAxis = [ True, True, False, False]
        nXTixks = 30
        nYTicks = [ 10, 10, 10, 10 ]
        lineColors = ['red', 'green', 'blue', 'magenta']
        plotType = [ 'line', 'line', 'line', 'line' ]
        drawZero = [ False, False, False, False ]
        plotAnalytics.setup(borderSize, addYAxis, nXTixks, nYTicks, lineColors, plotType, drawZero)
        
        # remove y bias
        stprices_close_zero = stprices_close[0]
        for i in range (0,  len(stprices_close)):
            stprices_close[i] -= stprices_close_zero
            
        # line fitting
        covOrth = int(self.covorth_value.get())
        lines = self.lineFit.fit(stprices_close, covOrth)
                     
        # band pass filter
        fs = 1.0 # sample frequency [samples / day]
        T = len(stprices_close) # sampletime [days]
        nsamples = int(fs * T)
         
        lowcut = int(self.bandpass_low.get())
        lowcut /= 1000.0
        highcut = int(self.bandpass_high.get())
        highcut /= 1000.0
        stprices_close_filtered = self.stockMath.apply_bandpass_filter(stprices_close, lowcut, highcut, fs)
        plotAnalytics.setXMax(nsamples)
        for i in range (0, nsamples):
            pnt = [stprices_close[i], stprices_close_filtered[i], 0, 0]
            plotAnalytics.addPoints(pnt, i)
            
        for i in range(0, len(lines)):
            plotAnalytics.addLine(lines[i])
        
        plotAnalytics.redraw()
        
        # FFT
        active = [True, False, False, False]
        plotFFT = PlotXY(self.frameFFT, active)
        borderSize = [ 0.1, 0.1, 0.1, 0.1 ]
        addYAxis = [ True, False, False, False]
        nXTicks = 30
        nYTicks = [ 10, 10, 10, 10 ]
        lineColors = ['red', 'green', 'blue', 'magenta']
        plotType = [ 'line', 'line', 'line', 'line' ]
        drawZero = [ False, False, False, False ]
        plotFFT.setup(borderSize, addYAxis, nXTicks, nYTicks, lineColors, plotType, drawZero)
        
        ndays = 720
        stprices_close = self.getStockprice(stock_name, ndays)
        
        # remove mean
        mean = 0.0
        for i in range(0, len(stprices_close)):
            mean += stprices_close[i]
        mean /= len(stprices_close)
        for i in range(0, len(stprices_close)):
            stprices_close[i] -= mean
        
        N = len(stprices_close)
        T = 1.0
        x = np.linspace(0.0, N * T, N)
        yf = fft(stprices_close)
        xf = np.linspace(0.0, 1.0 / (2.0 * T), int(N / 8.0)) # zoom to start of data
        yfft = 2.0 / N * np.abs(yf[0 : int(N / 2.0)])
        
        yfft[0] = 0.0
        yfft[1] = 0.0
        yfft[2] = 0.0
                
        plotFFT.setXMax(len(xf))   
        for i in range (0, len(xf)):
            pnt = [yfft[i], 0, 0, 0]
            plotFFT.addPoints(pnt, i)
            
        plotFFT.redraw()
        
        # market cap, dividend rate
        stockprices = self.pricedata[stock_name]['prices']
        lastPrice = stockprices[-1]
        try:
            mcap = lastPrice['marketCap']
            divRate = lastPrice['dividendRate']
            currency = lastPrice['currency']
            self.addInfo.set('cap:' + str(round((mcap / 1.0E9), 2)) + ' Mrd.' + currency + ' div:' + str(divRate))
        except(KeyError, ValueError):
            self.addInfo.set('-')
