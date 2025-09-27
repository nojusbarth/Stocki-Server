from modelupdates import ModelUpdater
from shared.logger import setup_logging
import threading
import time
import logging
import sys
from modelupdates import ModelUpdateScheduler

def runModelUpdater(updateQueue, predictionQueue, stopEvent, num_cores):
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    setup_logging()

    print("ModelUpdater process started", flush=True)

    # Scheduler initialisieren
    scheduler = ModelUpdateScheduler.ModelUpdateScheduler(
        updateQueue=updateQueue,
        predictionQueue=predictionQueue,
        stopEvent=stopEvent,
        num_cores=num_cores
    )

    # Scheduler starten (blockierend)
    scheduler.run()

    print("ModelUpdater process ended", flush=True)
