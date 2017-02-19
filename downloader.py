
import settings

import requests
import os
import datetime
import logging
from subprocess import call


class DataDownloader:

    def __init__(self, instrument, start_date, end_date, folder_storage="./data"):
        self.instrument = instrument
        self.start_date = start_date
        self.end_date = end_date
        self.folder_storage = folder_storage
        if not os.path.exists(self.folder_storage):
            os.mkdir(folder_storage)

    def _get_file(self, url, dest_dir='./'):
        local_filename = os.path.join(dest_dir, url.split('/')[-1])
        logging.warning("Downloading: %s", local_filename)
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return local_filename


class ForexiteDownloader(DataDownloader):
    """ data from https://www.forexite.com"""

    # "https://www.forexite.com/free_forex_quotes/2016/03/240316.zip"
    BASE_URL = "https://www.forexite.com/free_forex_quotes/%s"

    def __init__(self, start_date, end_date):
        super().__init__(None, start_date, end_date)
        self.folder_storage = os.path.join(self.folder_storage, 'forexite')
        if not os.path.exists(self.folder_storage):
            os.mkdir(self.folder_storage)

    def download_data(self):
        current_date = self.start_date
        while current_date < self.end_date:
            if current_date.isoweekday() != 6:
                url = self.BASE_URL % current_date.strftime("%Y/%m/%d%m%y.zip")
                self._get_file(url=url, dest_dir=self.folder_storage)
            current_date = current_date + datetime.timedelta(days=1)
        self._decompress_clean_zips()

    def _decompress_clean_zips(self):
        call(["unzip -n '%s/*.zip' -d %s" % (self.folder_storage, self.folder_storage)], shell=True)
        call(["rm %s/*.zip" % self.folder_storage], shell=True)


if __name__ == '__main__':
    fd = ForexiteDownloader(datetime.datetime.now() - datetime.timedelta(days=12),
                       datetime.datetime.now() - datetime.timedelta(days=1))
    fd.download_data()
