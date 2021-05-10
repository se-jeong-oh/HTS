import pybithumb
import basicfunc
import os


# 변동성 돌파 전략 계수
VB_coef = 0.3
# 확실하게 돌파했는지
VBreak = 1.000

# class Worker(QThread):
#     def __init__(self):
#         super().__init__()
#
#
# class VBFinder(Worker):
#     def __init__(self, tickers):
#         super().__init__()
#         self.tickers = tickers
#
#     def run(self, tickers):
#         good_tickers = []
#         diff = []
#         length = len(tickers)
#         for ticker in tickers:
#             idx = tickers.index(ticker)
#             target_price = get_target_price(ticker)
#             current_price = pybithumb.get_current_price(ticker)
#             if target_price < current_price:
#                 good_tickers.append(ticker)
#                 dif = (current_price - target_price) / target_price
#                 diff.append(dif)
#             print("Finding Ticker (Votability BreakThrough)...", idx, "/", length)
#
#         return good_tickers, diff
#
#
# class BullFinder(Worker):
#     def __init__(self, all_tickers):
#         super().__init__()
#         self.all_tickers = all_tickers
#
#     def run(self, all_tickers):
#         tickers = all_tickers
#         good_tickers = []
#         length = len(tickers)
#         for idx, ticker in enumerate(tickers):
#             check = 0
#             data = pybithumb.get_ohlcv(ticker)
#             price = pybithumb.get_current_price(ticker)
#
#             for num in range(2, 21):
#                 last_ma = basicfunc.sum_moving_avg(num, data, 1)
#                 if last_ma == -1:
#                     check = 0
#                     break
#                 if price > last_ma:
#                     check = 1
#                 else:
#                     check = 0
#                     break
#             if check == 1:
#                 good_tickers.append(ticker)
#             print("Processing: ", idx + 1, " / ", length)
#
#         return good_tickers


class OrderList():
    def __init__(self, data):
        self.ticker = data['order_currency']
        self.price = data['order_price']
        self.tot = data['contract'][0]['total']
        self.type = data['type']
        # self.gain_loss = 0

    # def get_gain_loss(self, money):
    #     self.gain_loss = money

    def print_order(self):
        if self.type == 'bid':
            print("<매수 주문> |", " Ticker Name : ", self.ticker, " |  Order Price : ", self.price, " |  Total : ", self.tot)
        else:
            print("<매도 주문> |", " Ticker Name : ", self.ticker, " |  Order Price : ", self.price, " |  Total : ", self.tot)



def get_target_price(ticker, state):
    df = pybithumb.get_ohlcv(ticker)
    yesterday = df.iloc[-2]

    today_open = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']
    target = today_open + state * (yesterday_high - yesterday_low) * VB_coef

    return target


def buy_crypto_currency(bithumb, ticker, sum_div, curr_ticker):

    left_ticker = sum_div - curr_ticker
    if left_ticker == 0:
        return -1
    krw = basicfunc.get_left_krw(bithumb, basicfunc.commission)
    if left_ticker != 1:
        krw = int(krw / left_ticker)
    unit, sell_price = basicfunc.maximum_units(ticker, krw)
    unit = int(unit * 10000) / 10000
    if int(sell_price) - (sell_price * 100) / 100 == 0:
        sell_price = int(sell_price)
    order = bithumb.buy_limit_order(ticker, sell_price, unit)
    return order


def sell_crypto_currency(bithumb, ticker):
    unit = bithumb.get_balance(ticker)[0]
    order = bithumb.sell_market_order(ticker, unit)

    return order


def find_ticker(tickers, option):
    good_tickers = []
    diff = []
    length = len(tickers)
    for ticker in tickers:
        idx = tickers.index(ticker)
        current_price = pybithumb.get_current_price(ticker)
        data = pybithumb.get_candlestick(ticker, chart_intervals="1h")
        if option == 'upper':
            target_price = get_target_price(ticker, 1)
            # 돌파 여부를 조금 더 확실하게
            if target_price * VBreak < current_price:
                # 1시간에 7% 상승은 너무 급격하다.
                if data.iloc[-1]['low'] > current_price * 0.92:
                    good_tickers.append(ticker)
                    dif = (current_price - target_price) / target_price
                    diff.append(dif)

        elif option == 'lower':
            target_price = get_target_price(ticker, -1)
            if target_price * (2 - VBreak) < current_price:
                # 1시간에 8% 하락은 너무 급격하다.
                if data.iloc[-1]['high'] < current_price * 1.08:
                    good_tickers.append(ticker)
                    dif = (current_price - target_price) / target_price
                    diff.append(dif)

        length = len(tickers)
        rate = int((idx + 1) * 100 / length)
        os.system("cls")
        print("Finding Ticker (Votability BreakThrough)... ", rate, "%")

    return good_tickers, diff


def recommend_ticker(tickers, option):

    # worker_vb = VBFinder(tickers)
    # worker_bull = BullFinder(tickers)
    # good_ticker_vb = worker_vb.start()
    # good_ticker_bull = worker_bull.start()
    #good_ticker_bull = basicfunc.check_bull_ticker(tickers)
    if option == "upper":
        good_ticker_bull = basicfunc.check_bull_ticker(tickers)
        good_ticker_vb, diff_vb = find_ticker(good_ticker_bull, option)
    else:
        good_ticker_vb, diff_vb = find_ticker(tickers, option)

    return good_ticker_vb, diff_vb
