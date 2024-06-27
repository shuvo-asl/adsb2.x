# library modules
import asyncio
import logging
from logging.handlers import QueueHandler,QueueListener
from queue import Queue

# helper coroutine to setup and manage the logger
async def init_logger():
    """ Initialise async root logger """
    # get the root logger
    log = logging.getLogger()
    # create the shared queue
    que = Queue()
    # add a handler that uses the shared queue
    log.addHandler(QueueHandler(que))
    # log all messages, debug and up
    log.setLevel(logging.DEBUG)
    # create a listener for messages on the queue
    logformatter = logging.Formatter('%(asctime)s|%(levelname)s|%(name)s|%(message)s')
    loghandler = logging.StreamHandler()
    loghandler.setFormatter(logformatter)
    listener = QueueListener(que, loghandler)
    try:
        # start the listener
        listener.start()
        # report the logger is ready
        logging.debug('Logger has started')
        # wait forever
        while True:
            await asyncio.sleep(60)
    # on application exit (stop task exception is raised)
    finally:
        # report the logger is done
        logging.debug('Logger is shutting down')
        # ensure the listener is closed
        listener.stop()

LOGGER_TASK = None
async def start_logger():
    """ Start logger and keep hard reference to task """
    global LOGGER_TASK #pylint:disable=global-statement
    LOGGER_TASK = asyncio.create_task(init_logger())
    await asyncio.sleep(0)