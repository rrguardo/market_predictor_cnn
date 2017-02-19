import logging
import settings
import datetime
import time
import random
import sys
import pprint

from models import TickMinute
from models import Session
from sqlalchemy import func

# cafe CNN dep libs
import numpy as np
import lmdb
sys.path.insert(0, '/home/raul/Documents/git_repos_prv/caffe/python/')
import caffe

# binary with 4 options

MODEL_FILE = './predictor_data/model.b4.prototxt'
PRETRAINED = '/home/raul/Documents/git_repos_prv/data_tool/predictor_data/results2/krnet_bin4/krnet_quick_iter_6000.caffemodel.h5'
MEAN_FILE = './predictor_data/mean.binaryproto'

net = None


def init_module(mode='cpu'):
    global net
    if not net:
        if mode == 'cpu':
            caffe.set_mode_cpu()
        else:
            caffe.set_mode_gpu()
        net = caffe.Net(MODEL_FILE, PRETRAINED, caffe.TEST)

init_module()


def make_lmdb(total_images, data=[], output_file='out.lmdb', width=100, height=100, channels=3):
    map_size = (width*height*channels + 100) * total_images
    env_train = lmdb.open('bin4_train_lmdb', map_size=map_size)
    env_test = lmdb.open('bin4_test_lmdb', map_size=map_size)
    cnt_train = 0
    cnt_test = 0
    cnt = 0
    with env_train.begin(write=True) as txn:
        with env_test.begin(write=True) as txn_test:
            # txn is a Transaction object
            for item in data:
                try:
                    print(item)
                    datum = caffe.proto.caffe_pb2.Datum()
                    datum.channels = channels
                    datum.height = width
                    datum.width = height

                    out = item.lmdb_vector
                    datum.data = out.tostring()
                    datum.label = item.label
                    test = False
                    if random.randint(1, 5) == 1: # cnt % 5 == 1:
                        # 20% to test
                        test = True
                        str_id = '{:08}'.format(cnt_test)
                        cnt_test += 1
                        txn_test.put(str_id.encode('ascii'), datum.SerializeToString())
                        #if cnt_test > 10000:
                        #    break
                    else:
                        # 80% to train
                        str_id = '{:08}'.format(cnt_train)
                        cnt_train += 1
                        txn.put(str_id.encode('ascii'), datum.SerializeToString())
                    cnt = cnt + 1
                except Exception as ex:
                    logging.error("Error processing %s, info: %s", item, ex)
    print("cnt: ", cnt, ", cnt_test: ", cnt_test, ", cnt_train: ", cnt_train)
    logging.info("Success!")


LABELS_MAP = {
    0: 'buy15p',
    1: 'sell15p',
    2: 'buysel15p'
}

LABELS_MAP_R = {
    'buy15p': 0,
    'sell15p': 1,
    'buysel15p': 2
}


class LMDBItem:
    """ Contains one time-frame with 10 hours of data as red, green, blue and the result label."""

    def __init__(self, raw_data, label, size=3*100*100, date_obj=None):
        narr = np.array(raw_data)
        red = narr[:, 0]
        green = narr[:, 1]
        blue = narr[:, 2]
        vect = list(red) + list(green) + list(blue)
        if len(vect) < size:
            vect += [0]*(size - len(vect))
        self.time = date_obj  # time.mktime(date_obj.timetuple())
        self.lmdb_vector = np.array(vect, np.uint8)
        self.label = label
        #print(self)

    def __repr__(self):
        return "<LMDBItem(time: %s, label: %s, len: %s, data: %s)>" % (self.time, self.label,
                                                                       len(self.lmdb_vector), self.lmdb_vector)


class DataBuilder:

    # 10 hours timeframe in minutes
    frame_minutes = 600
    pip = 0.01

    def __init__(self):
        self.session = Session()
        self.start_date = datetime.datetime.now() - datetime.timedelta(days=78)

    def get_date_vector(self, _date):
        """ Get the  lmdb vector for predictions"""
        rgb_data = []
        raw_ticks = self.session.query(TickMinute).filter(TickMinute.tick_date <= _date).order_by(
            TickMinute.tick_date.desc()).limit(self.frame_minutes)
        total_ticks = raw_ticks.count()
        if total_ticks != self.frame_minutes:
            raise Exception("No enough data")
        data = [x for x in raw_ticks]
        data.reverse()
        for item in data:
            try:
                #print(item)
                rgb_data += item.get_rgb_encoded()
            except Exception as ex:
                logging.error("Error: %s. item: %s", ex, item)
                raise ex
        #print(rgb_data[:15])
        return LMDBItem(date_obj=data[0].tick_date, raw_data=rgb_data, label=-1)

    def data_iterator(self):
        while True:
            rgb_data = []
            raw_ticks = self.session.query(TickMinute).filter(TickMinute.tick_date>self.start_date).order_by(
                TickMinute.tick_date.asc()).limit(self.frame_minutes)
            total_ticks = raw_ticks.count()
            if total_ticks != self.frame_minutes:
                break
            # now get RGB
            last_tick = None
            for item in raw_ticks:
                try:
                    if not last_tick:
                        last_tick = item
                    rgb_data += item.get_rgb_encoded()
                except Exception as ex:
                    logging.error("Error: %s. item: %s", ex, item)
                    raise ex
            self.start_date = last_tick.tick_date
            #print(rgb_data)
            label = self.calc_label(last_tick.tick_date, last_tick.close)
            #print("Label: %s"  % label)
            yield LMDBItem(date_obj=last_tick.tick_date, raw_data=rgb_data, label=label)

    def get_tick_close(self, tick_date):
        try:
            result = self.session.execute("""
                SELECT close, tick_date
                FROM tick_minute
                WHERE tick_date >= :dt1
                ORDER BY tick_date ASC
                LIMIT 1
            """, {'dt1': tick_date})
            res = result.fetchone()
            close = res[0]
            return (float(close), res[1])
        except Exception as ex:
            logging.warning("Lost close tick %s", tick_date)
            return -1

    def calc_label(self, tick_date, tick_close, minutes=60, profit=20.0):
        try:
            #print("Close: ", tick_close)
            result = self.session.execute("""SELECT MAX(high) AS max_vals, MIN(low) AS min_vals
                                             FROM (SELECT high, low
                                                    FROM tick_minute
                                                    WHERE tick_date > :dt1
                                                    ORDER BY tick_date ASC
                                                    LIMIT :minutes
                                                    ) sbt
                                           """,
                                          {'dt1': tick_date, 'minutes': minutes})
            res = result.fetchone()
            rmin = float(res[1])
            rmax = float(res[0])
            tick_close = float(tick_close)
            #print("Min: ", rmin, "  Max: ", rmax, " Close: ", tick_close)
            brate = rmax - tick_close
            srate = tick_close - rmin
            if srate <= 0 or srate <= brate:
                #buy
                if srate <= 0 or brate/srate >= 2:
                    #strong buy
                    return 0
                else:
                    #weak buy
                    return 1
            if brate <= 0 or brate < srate:
                # sell
                if brate <= 0 or srate/brate >= 2:
                    # strong sell
                    return 2
                else:
                    # weak sell
                    return 3
            raise ValueError("This should never happen")
        except Exception as ex:
            logging.error("calc_label fail for: %s", ex)
            return 1


class Predictor:
    width = 100
    height = 100

    def __init__(self):
        self.db = DataBuilder()

    def date_predictor(self, _date):
        vobj = self.db.get_date_vector(_date)
        #print(vobj.lmdb_vector)
        return self.cnn_predict(vobj.lmdb_vector)

    def search_pattern(self, start_date, end_date, buy_threshold=0.2368, sell_threshold=0.3719):
        td = datetime.timedelta(minutes=1)
        cdate = start_date
        max_b = []
        max_s = []
        while True:
            cpred = self.date_predictor(cdate)
            tick_close, check_cdate = self.db.get_tick_close(cdate)
            if check_cdate != cdate:
                logging.warning("Hollow detected jump to %s", check_cdate)
                cdate = check_cdate
            clabel = self.db.calc_label(cdate, tick_close=tick_close)
            max_b.append((cpred[0] + cpred[1] - cpred[2] - cpred[3], cdate, clabel))
            max_s.append((cpred[2] + cpred[3] - cpred[0] - cpred[1], cdate, clabel))
            print("Date: ", cdate.isoformat(), ", Prob: ", cpred, ", Label: ", clabel)
            #pred =False
            #if cpred[0] >= buy_threshold:
            #    pred = True
            #    print("Buy op at: ", cdate, ", Prob: ", cpred, ", Label: ", clabel)
            #if cpred[1] >= sell_threshold:
            #    pred = True
            #    print("Sell op at: ", cdate, ", Prob: ", cpred, ", Label: ", clabel)
            #if not pred:
            #    print("no pattern at: ", cdate, ", Prob: ", cpred, ", Label: ", clabel)
            cdate += td
            if cdate > end_date:
                break
        max_b.sort(key=lambda x: x[0], reverse=True)
        max_s.sort(key=lambda x: x[0], reverse=True)
        print("Max Strong Buys: ")
        total = max(10, int(len(max_b)/180))
        print(total)
        pprint.pprint(max_b[:total])
        print("+++++++++++++++++++++++++++")
        print("Max Strong Sells: ")
        total = max(10, int(len(max_s)/180))
        print(total)
        pprint.pprint(max_s[:total])

    @staticmethod
    def cnn_predict(input_data, do_print=False):
        global net

        out = input_data
        out = out.reshape(1, 3, Predictor.width, Predictor.height)
        #print(out)

        net.blobs['data'].data[...] = out
        out = net.forward()
        if do_print:
            # print net.blobs['prob'].data
            print([round(i, 2) for i in out['prob'][0]])
        return out['prob'][0]


if __name__ == "__main__":
    if "build" in sys.argv:
        db = DataBuilder()
        #for item in db.data_iterator():
        #    print(item)
        make_lmdb(total_images=700*60*24, data=db.data_iterator(), output_file='out.lmdb')
    elif "predict" in sys.argv:
        start_date = datetime.datetime(year=2017, month=1, day=3, hour=0, minute=0, second=0)
        end_date = datetime.datetime(year=2017, month=1, day=11, hour=23, minute=59, second=0)
        pred = Predictor().search_pattern(start_date, end_date)
    else:
        print("enter command: build, predict, ...")
