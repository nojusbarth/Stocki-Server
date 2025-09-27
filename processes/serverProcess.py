from api.server import Server
from shared.logger import setup_logging
import logging
import threading
import time
import sys

def runServer(predictionQueue, stopEvent):
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    setup_logging()

    print("server up --------------", flush=True)
    server = Server(predictionQueue=predictionQueue)

    try:
        server.start()
    except KeyboardInterrupt:
        stopEvent.set()




