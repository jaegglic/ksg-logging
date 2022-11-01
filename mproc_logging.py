"""Demonstrates a basic example of logging in multiple processes."""
import queue
from pathlib import Path
import logging
import logging.handlers
import multiprocessing
from random import choice, random
import time


FMT = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(message)s')
FILENAME = f'{Path(__file__).stem}.log'

LOGGERS = ['banana', 'ghostwriter', 'superman']
LEVEL = logging.DEBUG

FILEROTATION_MAXBYTES = 5000
FILEROTATION_NBACKUPS = 3


def listener_configurer():
    """Configuration of the listener process"""
    fh = logging.handlers.RotatingFileHandler(FILENAME, 'a', FILEROTATION_MAXBYTES, FILEROTATION_NBACKUPS)
    fh.setFormatter(FMT)
    logging.getLogger().addHandler(fh)


def listener_process(queue: queue.Queue, configurer: callable):
    """Listener process lop-level loop.

    Here we wait for logging events stacket into the queue and handle them; quit when you get a None.
    """
    configurer()
    while True:
        try:
            # Get and remove the oldest log-record (FIFO queue)
            record = queue.get()        # type: logging.LogRecord
            if record is None:
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except Exception:
            import sys, traceback
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def worker_configurer(queue: queue.Queue):
    """The worker configuration is done at the start of the worker process run.

    This mainly adds the queue for handling the logs. Log messages are then added in the form of ``logggin.LogRecords`
    objects to the `queue.
    """
    qh = logging.handlers.QueueHandler(queue)
    root_logger = logging.getLogger()
    root_logger.addHandler(qh)
    root_logger.setLevel(logging.DEBUG)


def worker_process(queue: queue.Queue, configurer: callable):
    """Worker process top-level loop.

    Here we do nothing but wait a random number of seconds between 0 and 1 and log the waited time.
    """
    configurer(queue)
    name = multiprocessing.current_process().name
    for i in range(10):
        sleeping_time = random()
        time.sleep(sleeping_time)
        logger = logging.getLogger(choice(LOGGERS))
        message = f'Child proces "{name}" step {i}: slept for {sleeping_time}[s] '

        # Add `logging.LogRecord` to the queue
        logger.log(LEVEL, message)


def main():
    """Orchestration of this demonstration.

    Single steps are
        - Create queue
        - Create and start the listener process
        - Create and start 10 worker processes
        - Wait for all workers to finish
        - Stop the listener process
    """
    # Create queue
    queue = multiprocessing.Queue(-1)

    # Create and start listener process
    listener = multiprocessing.Process(target=listener_process, args=(queue, listener_configurer))
    listener.start()

    # Create and start 10 worker processes
    workers = []
    for _ in range(10):
        wrk = multiprocessing.Process(target=worker_process, args=(queue, worker_configurer))
        workers.append(wrk)
        wrk.start()

    # Wait for all workers to finish
    for wrk in workers:
        wrk.join()

    # Stop the listener process
    queue.put_nowait(None)
    listener.join()


if __name__ == '__main__':
    main()
