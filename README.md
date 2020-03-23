# market_predictor_cnn
Software tools to predict market movements using convolutional neural networks.

The basic idea is encode market data as RGB pixels for train CNN to predict market movements and detect patterns.
CNN framework caffe was used.

Good results was observed training the CNN to detect when the price will drop 20 pips in next 60 minutes.
In CNN top 10 positions detected in ~7 days, we observe ~70% correct predictions, ~10% incorrect prediction,
~20% neutral predictions (not profit loss).

# Usage

Current software only analyze `USDJPY` but it was code to be adapted easy to any trade item.

## Install requirements

- python3.5
- caffe framework with python3.5 bindings
- pip install -r requirements.txt

## Database initial setup

1. Adjust database settings at file `settings.py`.
2. Run command `python models.py` to create required table at database.

## Download Historical Data.

`python downloader.py` This command will start the download of historical data (forexite.com is used) for the past 12
days. The script can be modified easy to allow download more data.

Under folder `data/forexite/` all the market data downloaded will be stored.

## Pre-Process Historical Data

After download the data we need load it to local database, this is done by a single command.

- `python multicore_tasks.py csv data/forexite/`

## Create training and testing data for CNN

This research cover 4 distinct ways to train the CNN according to 4 similar CNN Net.
Is recommended train the CNN with less than 1 month of data in current software.

### Case binary buy, sell after 60 minutes.

To create the train and test file run this command `python lmdb_processor_bin2.py build`, adjust lmdb_processor
script with the correct estimate of images that will be generated and the dates ranges.

#### Lmdb files will be generated:

- `bin_test_lmdb` this is the testing set
- `bin_train_lmdb` this is the training set

## Train a CNN with market data

At repo under folder `caffe_trainer/` is located the caffe Nets used to generate the trained CNN.

## Forecast next market movement using trained CNN

- Adjust `lmdb_processor_` script to load use the trained CNN.
- Run predictor `python lmdb_processor_bin2.py predict`

# Best results:

## Case sell, undef >20 pips in 60 minutes (direct prob):
SELL
For top 10 (top 20%), we see this good results: profit:  60% positive money profit. 70% positive,  10% negative, 20%
real neutrals
For top 25 (top 50%), we see yet ~25% profit.

## Case buy, sell, undef >20 pips in 60 minutes (diff prob buy-sell, sell-buy):***
SELL
60% positive, 
0% negative
40% real neutrals
profit: ~60%

For top 25 (top 50%), we see yet ~30% profit.

## Case binary buy, sell after 60 minutes:
BUY**
80% positive, 
20% negative
profit: ~60%
For top 25 (top 50%), we see same 80% positive, 60% profit

## Case binary4  buys-sells, sells-buys after 60 minutes:
BUY
positive: 80%
negative: 20%
profit: 60%
For top 25 (top 50%), we see 16ok, 9ko,  ~25% profit yet

## Case sigmoid buy, sell, undef >20 pips in 60 minutes (diff prob buy-sell, sell-buy):
SELL
if inverted profit ~100%, For top 25 (top 50%), we see good accuracy. (non-sense here)

# Conclusions  
Case buy, sell, undef >20 pips in 60 minutes (diff prob buy-sell, sell-buy) was the best predictor for SELL
positions(60% profit). Profit decrease here to 30% using top 25(50%).
Case binary buy, sell after 60 minutes, was the best predictor for BUY positions(60% profit remain using top
10 and top 25).

While this reasearch aparently show good result at studied time frame, the best pattern was not observed again.
And same study at distict time frames change the results. The this ends just as a complex gamble game.



