# 🥸 Logging with Python

## 📱 Generic setup
1. Make sure `python-venv` is installed
    ```commandline
    python --version                    # Gets your python version X.Y
    sudo apt install pythonX.Y-venv     # Replace X.Y with your version
    ```

2. Get the repo from `github`
    ```commandline
    cd <your-path>/
    git clone https://github.com/smc40/ksg-logging.git
    cd ksg-logging/
    ```

3. Make and activate `venv`
   ```commandline
   python -m venv venv
   source venv/bin/activate
   ```

## 🎚️ Logging Level
![Level](logging_level.png)

## 🕹️ Default behavior
```commandline
$ python default_logging.py       # Writes the logs in a file 'default_logging.log'
```
---
Under other, withing the `basicConfig` you can specify the logging format
```python
import logging

format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=format)
```
as well as the [date format](https://www.w3schools.com/python/gloss_python_date_format_codes.asp)
```python
import logging

datefmt = '%a %d %b %Y %H:%M:%S'
logging.basicConfig(datefmt=datefmt)
```
NOTE: The default logging threshold level is set to "WARNING". This means that the logger only logs messages with the
level of WARNING or above (i.e. WARNING, ERROR, CRITICAL). We can set the threshold as follows:
```python
import logging

logging.basicConfig(level='DEBUG')
```
which would cause ALL messages of ANY LEVEL to be logged.

## 👻 Handler driven
```commandline
python handler_logging.py       # Writes the logs in a file 'handler_logging.log'
```
---
Let us define two different logging handlers:
1. Logging to a given file (level=WARNING)
2. Logging to the console (level=DEBUG)

For this we use `handlers`
```python
import logging
from pathlib import Path

fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Logging to file
filename = f'{Path(__file__).stem}.log'
file_handler = logging.FileHandler(filename=filename)
file_handler.setFormatter(fmt=fmt)
file_handler.setLevel(level='WARNING')

# Logging to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(fmt=fmt)
console_handler.setLevel(level='DEBUG')

# Set the basic config for all the subsequent loggers.
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])
```
NOTE: It is crucial to set the level in `logging.basicConfig` to be LOWER or EQUAL to the lowest level of any handler. 
Otherwise, the basic config will reject the log message before sending it to the handlers.

## 🎡 Rotating File
```commandline
python rotating_logging.py          # Using rotating log files
```
---
As a system writes information to log files, the log file grows in size. We use log rotation to avoid large files that 
could create issues when opening them, which transfers log events to a new log file without interrupting the logging 
process. In many cases, the process involves renaming the current file to something new and then naming the new file 
the first file’s name. 
```python
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

filename = f'{Path(__file__).stem}.log'
fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
rh = RotatingFileHandler(filename=filename, maxBytes=300, backupCount=10)
```
The `maxBytes` sets an upper limit for file size whereas `backupCount` us the maximum number of files to be generated.

## 🎶 Multiprocessing
```commandline
python -m pckg.mproc_logging       # Writes the logs in a file 'pckg_logging.log'
```
---
Logging to a single file from multiple processes is very well explained [here](https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes).
Another explanation for the three different approaches mentioned above can be found [here](https://superfastpython.com/multiprocessing-logging-in-python/).

_Although logging is thread-safe, and logging to a single file from multiple threads in a single process is supported, 
logging to a single file from multiple processes is not supported, because there is no standard way to serialize 
access to a single file across multiple processes in Python._

In this example we will use `multiprocessing.Queue` in order to communicate between processes. A separate listener
process listens for events sent by other processes and logs them according to its own logging configuration.

### `multiprocessing.Queue`
The [`Queue`](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Queue) is a FIFO 
(first-in-first-out) queue modeled on the `queue.Queue` class in the standard library.
- **`put(obj, block=True)`**: Put obj into the queue. If the `block` is `True` and `timeout` is `None` block if 
necessary until a free slot is available.
- **`put_nowait()`**: Equivalent to `put(obj, block=False)`
- **`get(obj, block=True)`**: Remove and return an item from the queue. If optional args `block` is `True` block if 
necessary until an item is available.
- **`get_nowait()`**: Equivalent to `get(False)`

```commandline
                           (communication)
    process_0 (logging) ────────|
    process_1   (work)  ────────|
    process_2   (work)  ────────|  
       ...                      |
    process_n-1 (work)  ────────|
```
Because you'll want to define the logging configurations for listener and workers, the listener and worker process 
functions take a configurer parameter which is a callable for configuring logging for that process. These functions 
are also passed the queue, which they use for communication.


```python
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
```

PS: @Nico -> !!! ABFAHRE !!!