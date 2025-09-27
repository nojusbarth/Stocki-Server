import tkinter as tk
from tkinter import ttk
from api.server import Server
from shared.ml.prediction import Predictor
from shared.ml.ModelManager import ModelManager
from shared.data import StockManager
from shared.ml.prediction.repository import PredictionRepository
from processes import serverProcess
from processes.modelProcess import runModelUpdater
from processes.serverProcess import runServer
from processes.stockProcess import runStockUpdater
from view import MainFrame
from windowMng import *
import threading
import time
import atexit
from multiprocessing import Process, Queue, cpu_count, Event
from shared.logger import setup_logging
import psutil
import os
import sys
import multiprocessing
from multiprocessing import set_start_method
from shared.data import StockUpdateInfo
from datetime import datetime, timezone


def set_affinity(proc, cores):
    psutil.Process(proc.pid).cpu_affinity(cores)

if __name__ == "__main__":
    setup_logging()
    try:
        multiprocessing.set_start_method("spawn")
    except RuntimeError:
        pass

    updateQueue = Queue()
    predictionQueue = Queue()
    stopEvent = Event()

    num_logical_cores = psutil.cpu_count(logical=True)
    print("Logische Kerne:", num_logical_cores)

    # Kerne reservieren:
    # 0 = Main (Server + Log), 1 = StockUpdater, 2+3 = frei, Rest für ModelUpdater
    modelUpdater_cores = list(range(4, num_logical_cores))
    num_cores_for_modelUpdater = len(modelUpdater_cores)

    stockUpdaterProcess = Process(
        target=runStockUpdater,
        args=(updateQueue, stopEvent)
    )
    modelUpdaterProcess = Process(
        target=runModelUpdater,
        args=(updateQueue, predictionQueue, stopEvent, num_cores_for_modelUpdater)
    )

    #stockUpdaterProcess.start()
    modelUpdaterProcess.start()

    set_affinity(stockUpdaterProcess, [1])
    set_affinity(modelUpdaterProcess, modelUpdater_cores)

    try:
        #server blockiert main
        runServer(predictionQueue, stopEvent)
    except KeyboardInterrupt:
        stopEvent.set()

        stockUpdaterProcess.join(timeout=5)
        modelUpdaterProcess.join(timeout=5)

        if stockUpdaterProcess.is_alive():
            print("[Main] Forcing stockUpdaterProcess to terminate")
            stockUpdaterProcess.terminate()
        if modelUpdaterProcess.is_alive():
            print("[Main] Forcing modelUpdaterProcess to terminate")
            modelUpdaterProcess.terminate()

        stockUpdaterProcess.join()
        modelUpdaterProcess.join()