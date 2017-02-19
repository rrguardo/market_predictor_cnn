import settings
from multiprocessing import Pool, TimeoutError
import time
import os
import sys
from csv_parser import ForexiteParserPoolWorker


def do_multicore_task(funct_task, data=[], processes=8):
    with Pool(processes=processes) as pool:
        return pool.map(funct_task, data)


def mult_data(x):
    return x*x


if __name__ == '__main__':
    # start 4 worker processes
    if "csv" in sys.argv:
        data = ForexiteParserPoolWorker.get_data(sys.argv[2])
        do_multicore_task(ForexiteParserPoolWorker.worker_func, data)
    elif "download" in sys.argv:
        data = ForexiteParserPoolWorker.get_data(sys.argv[2])
        do_multicore_task(ForexiteParserPoolWorker.worker_func, data)
    else:
        print(do_multicore_task(funct_task=mult_data, data=range(0, 20)))
