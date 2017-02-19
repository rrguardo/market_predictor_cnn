
import settings
import csv
import os
import datetime
from models import TickMinute
from models import Session
import logging


def read_csv_file(src_file, newline='', delimiter=',', quotechar=None):
    with open(src_file, newline=newline) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        for row in spamreader:
            yield row


class ForexiteParserPoolWorker:

    @staticmethod
    def worker_func(cfile, tick_filter=['USDJPY']):
        session = Session()
        cnt = 0
        logging.warning("Start processing: %s", cfile)
        reader = read_csv_file(cfile)
        for row in reader:
            try:
                row_data = [x for x in row]
                #logging.warning("Procesing: %s", row_data)
                # 20160501,232100
                if row_data[0] not in tick_filter:
                    continue
                cnt += 1
                tick_date = datetime.datetime.strptime(row_data[1] + "," + row_data[2], "%Y%m%d,%H%M%S")
                tick = TickMinute(
                    tick_date=tick_date,
                    ticker=row_data[0],
                    open=row_data[3],
                    high=row_data[4],
                    low=row_data[5],
                    close=row_data[6]
                )
                session.add(tick)
                if cnt%300 == 0:
                    session.commit()
            except Exception as ex:
                logging.error("Exception: %s", ex)
        session.commit()
        logging.warning("Done processing: %s", cfile)

    @staticmethod
    def get_data(src_dir):
        result = []
        for root, dirs, files in os.walk(src_dir, topdown=False):
            for name in files:
                result.append(os.path.join(src_dir, name))
        return result


class ForexiteParser:

    def __init__(self, src_dir):
        session = Session()
        for root, dirs, files in os.walk(src_dir, topdown=False):
            for name in files:
                cfile = os.path.join(src_dir, name)
                reader = read_csv_file(cfile)
                for row in reader:
                    try:
                        row_data = [x for x in row]
                        #logging.warning("Procesing: %s", row_data)
                        # 20160501,232100
                        tick_date = datetime.datetime.strptime(row_data[1] + "," + row_data[2], "%Y%m%d,%H%M%S")
                        tick = TickMinute(
                            tick_date=tick_date,
                            ticker=row_data[0],
                            open=row_data[3],
                            high=row_data[4],
                            low=row_data[5],
                            close=row_data[6]
                        )
                        session.add(tick)
                        session.commit()
                    except Exception as ex:
                        logging.error("Exception: %s", ex)


if __name__ == '__main__':
    import sys
    ForexiteParser(sys.argv[1])
