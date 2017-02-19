
import math
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL
from sqlalchemy.orm import sessionmaker
import settings


from settings import ENGINE

Session = sessionmaker(bind=settings.ENGINE)

Base = declarative_base()


class TickMinute(Base):
    __tablename__ = 'tick_minute'
    tick_date = Column(DateTime, primary_key=True)
    ticker = Column(String(32), primary_key=True)
    open = Column(DECIMAL(15,7))
    high = Column(DECIMAL(15,7))
    low = Column(DECIMAL(15,7))
    close = Column(DECIMAL(15,7))
    TICK_MAPS = [
        'AUDJPY',
        'AUDUSD',
        'CHFJPY',
        'EURCAD',
        'EURCHF',
        'EURGBP',
        'EURJPY',
        'EURUSD',
        'GBPCHF',
        'GBPJPY',
        'GBPUSD',
        'NZDJPY',
        'NZDUSD',
        'USDCAD',
        'USDCHF',
        'USDCZK',
        'USDJPY',
        'XAGUSD',
        'XAUUSD',
    ]

    def __repr__(self):
        return "<TickMinute( %s, %s, HIGH: %s, LOW: %s, OPEN: %s, CLOSE: %s)>" % (
            self.ticker, self.tick_date, self.high, self.low, self.open, self.close)

    @staticmethod
    def _encode_val(value):
        """
            Encode a tick value(open or high or low, etc) as 2 RBG pixels.
            One pixel for interger section and other pixel for fractional section.
        """
        fract, inte = math.modf(value)
        fract = str(int(fract*1000000))
        inte = str(int(inte))
        for i in range(0, 6-len(inte)):
            inte = "0" + inte
        for i in range(0, 6-len(fract)):
            fract = "0" + fract
        pix1 = (int(inte[:2]) + 100,
                int(inte[2:4]) + 100,
                int(inte[4:]) + 100)
        pix2 = (int(fract[:2]) + 100,
                int(fract[2:4]) + 100,
                int(fract[4:]) + 100)
        return [pix1, pix2]

    @staticmethod
    def _encode_date_and_ticker(value, ticker='USDJPY'):
        """
            Encode a date as 2 RGB pixels.
            Pixe 1 is (year, month, day)
            Pixel 2 is (weekday and ticker, hour, minute)
        """
        year = value.year%100
        month = value.month
        day = value.day
        pix1 = (year, month, day)

        # TODO! Separate ticker and week day in distinct pixels
        wd = value.weekday() + 100 + (TickMinute.TICK_MAPS.index(ticker) + 1)*10
        hour = value.hour
        minute = value.minute
        pix2 = (wd, hour, minute)
        return [pix1, pix2]

    def get_rgb_encoded(self):
        """
            Return the tick data encoded as 10 RGB pixels.
            In one 100x100 image we can encode ~16 hours
        """
        # TODO: Encode ticker for multi-currency
        ticker = self.ticker
        tick_date = self._encode_date_and_ticker(self.tick_date, ticker=ticker)
        open_ = self._encode_val(self.open)
        high = self._encode_val(self.high)
        low = self._encode_val(self.low)
        close = self._encode_val(self.close)
        #print(tick_date)
        return tick_date + open_ + high + low + close


if __name__ == '__main__':
    Base.metadata.create_all(ENGINE)
    #session = Session()
    #tk = session.query(TickMinute).filter_by(ticker='USDJPY').first()
    #print(tk)
    #print("+++++++++++++++++++++++++++++")
    #print(tk.get_rgb_encoded())
