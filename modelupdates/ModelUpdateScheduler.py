from multiprocessing import Manager, Pool
import queue
from modelupdates.ModelUpdater import ModelUpdater
import time

class ModelUpdateScheduler:
    def __init__(self, updateQueue, predictionQueue, stopEvent, num_cores=4):
        self.updateQueue = updateQueue
        self.predictionQueue = predictionQueue
        self.stopEvent = stopEvent
        self.num_cores = num_cores

    def run(self):
        print("ModelUpdateScheduler started", flush=True)
        manager = Manager()
        mp_predictionQueue = manager.Queue()
        try:
            with Pool(processes=self.num_cores) as pool:
                while not self.stopEvent.is_set():
                    tasks = []
                    while True:
                        try:
                            stocksInfo = self.updateQueue.get_nowait()
                            for stock in stocksInfo:
                                tasks.append((stock, mp_predictionQueue))
                        except queue.Empty:
                            break

                    if tasks:
                        # Pool parallel abarbeiten
                        for _ in pool.starmap(ModelUpdater.process_stock, tasks):
                            pass

                    # Ergebnisse zurück in die originale PredictionQueue
                    while not mp_predictionQueue.empty():
                        self.predictionQueue.put(mp_predictionQueue.get())

                    time.sleep(0.5)
        except KeyboardInterrupt:
            print("ModelUpdateScheduler interrupted, shutting down...", flush=True)
            self.stopEvent.set()
        finally:
            print("ModelUpdateScheduler ended", flush=True)



