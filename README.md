# market_predictor_cnn
Softwares tools to predict market movements using convolutional neural networks.

The basic idea is encode market data as RGB pixels for train CNN to predict market movements and detect patterns. CNN framework caffe was used.

Good results was observed training the CNN to detect when the price will drop 20 pips in next 60 minutes. In CNN top 10 positions detected in ~7 days, we observe ~70% correct predictions, ~10% incorrect prediction, ~20% neutral predictions (not profit loss).

# Best results:

## Case sell, undef >20 pips in 60 minutes (direct prob):
SELL
For top 10 (top 20%), we see this good results: profit:  60% positive money profit. 70% positive,  10% negative, 20% real neutrals
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
Case buy, sell, undef >20 pips in 60 minutes (diff prob buy-sell, sell-buy) was the best predictor for SELL positions(60% profit). Profit decrease here to 30% using top 25(50%).
Case binary buy, sell after 60 minutes, was the best predictor for BUY positions(60% profit remain using top 10 and top 25).
