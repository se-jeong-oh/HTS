import pybithumb
import basicfunc
import time

bithumb = basicfunc.bithumb_set()
sell_price = 6465
unit = 0.2573
poss = {}
data = pybithumb.get_candlestick("BTC", chart_intervals='1m')
print(data)
