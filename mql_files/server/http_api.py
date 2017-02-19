from flask import Flask, request
import hashlib
import logging
import datetime

app = Flask(__name__)



API_KEY = 'KH7jsdfR61j89HW23-123jknk3qw673pv7sdi+gFe'


def validate_request(tick_date, vhash):
    data = tick_date + API_KEY
    data = data.encode('utf-8')
    c_vhash = hashlib.sha1(data).hexdigest()
    if c_vhash != vhash:
        logging.error("Invalid vhash!")
        return False
    return True


@app.route('/tick_post', methods=['GET', 'POST'])
def hello_world():
    """
    Example request:
        /tick_post?ticker=USDJPY&tick_date=123&open=1&close=2&high=3&low=4&vhash=047f0f14f042ea0857fe04eabfb0d0aa3d7ae275
        /tick_post?ticker=USDJPY&tick_date=2017.01.18-06:19:00&open=113.091&close=113.091&high=113.091&low=113.091&vhash=85cd263665ee9f04f60044ce0fb52eba6a56278d
    """
    try:
        ticker = request.args['ticker'].upper()
        if ticker != "USDJPY":
            raise ValueError("ticker should be USDJPY")
        tick_date = request.args['tick_date']
        tick_date_obj = datetime.datetime.strptime(tick_date, "%Y.%m.%d-%H:%M:%S")
        open = float(request.args['open'])
        close = float(request.args['close'])
        high = float(request.args['high'])
        low = float(request.args['low'])
        vhash = request.args['vhash']
    except Exception as ex:
        logging.error("Error: ", ex)
        return "missing parameter!!"
    print("+++++++++++++++++++++++++++++++++++")
    print("Get data received: ", request.args)
    print("Date object: ", tick_date_obj)
    print("+++++++++++++++++++++++++++++++++++")
    if not validate_request(tick_date, vhash):
        return 'ERRROR: invalid vhash!'

    return '0'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
