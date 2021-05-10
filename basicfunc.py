import pybithumb
import pandas as pd
import datetime
import os
import time

# 빗썸 수수료
commission = 0.003
# 목표 수익률
alpha = 1.03


def bithumb_set():
    with open("bithumb.txt") as f:
        lines = f.readlines()
        key = lines[0].strip()
        secret = lines[1].strip()
        bithumb = pybithumb.Bithumb(key, secret)

    return bithumb


def basic_setting():
    """
    빗썸의 API를 활용하기 위한 함수.
    그 외에도 전역변수 설정이나, 기본적인 세팅을 하는 함수.
    :return: None
    """
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)


def print_detail():
    detail = pybithumb.get_market_detail("BTC")  # 저가, 고가, 평균 거래 금액, 거래량 -> 튜플 형식
    print(detail)


def print_bid():
    orderbook = pybithumb.get_orderbook("BTC")  # 시간, 지불 화폐, 주문 화폐, 매수 호가, 매도 호가
    bids = orderbook['bids']
    for bid in bids:
        price = bid['price']
        quant = bid['quantity']
        print("매수호가: ", price, "매수잔량: ", quant)


def print_time():
    orderbook = pybithumb.get_orderbook("BTC")  # 시간, 지불 화폐, 주문 화폐, 매수 호가, 매도 호가
    ms = int(orderbook['timestamp'])
    dt = datetime.datetime.fromtimestamp(ms / 1000)
    print(dt)


def print_closing_price():
    all = pybithumb.get_current_price("ALL")
    for ticker, data in all.items():
        print(ticker, data['closing_price'])


def sum_moving_avg(length, data, start):
    """
    이동평균을 구하는 함수
    :param length: 이동평균의 길이
    :param data: 이동평균을 시행할 데이터
    :param start: 시작할 일자(10일전의 데이터를 얻고 싶다면 10입력 / 인덱스 기준으로 어제가 [-1] 일 경우)
    :return: 이동평균된 값
    """
    try:
        last_price = 0
        for i in range(start, length+start):
            idx = -i
            last_price += data['close'][idx]
        last_price /= length
    except:
        last_price = -1
    return last_price


def check_bull_ticker(tickers):
    """
    상승장인 ticker를 파악하는 함수
    option : "upper" 상승장 파악
    :return: 상승장인 ticker가 포함된 리스트
    """
    good_tickers = []
    length = len(tickers)
    for idx, ticker in enumerate(tickers):
        check = 0
        data = pybithumb.get_ohlcv(ticker)
        price = pybithumb.get_current_price(ticker)

        for num in range(2, 21):
            last_ma = sum_moving_avg(num, data, 1)
            if last_ma == -1:
                check = 0
                break
            if price > last_ma:
                check = 1
            else:
                check = 0
                break
        if check == 1:
            good_tickers.append(ticker)

        length = len(tickers)
        rate = int((idx + 1) * 100 / length)
        os.system("cls")
        print("Finding Ticker (Bull Markets)... ", rate, "%")

    return good_tickers


def diff_ma_curr(tickers, number):
    """
    이동평균과 현재가의 차이를 구하는 함수
    :param tickers: 검색할 ticker들의 목록
    :param number: 이동평균의 길이(5일 이동평균이면 5)
    :return: 이동평균과 현재가의 차이, 이동평균 리스트, 이동평균 기울기 리스트
    """
    rt_diff = []
    rt_ma = []
    ma_slope = []
    for ticker in tickers:
        price = pybithumb.get_current_price(ticker)
        data = pybithumb.get_ohlcv(ticker)
        last_ma = sum_moving_avg(number, data, 1)
        last_ma_5 = sum_moving_avg(number, data, 5)
        rt_ma.append(last_ma)
        rate = (price - last_ma) * 100 / last_ma
        rt_diff.append(rate)
        slope = (last_ma - last_ma_5) * 100 / last_ma_5
        ma_slope.append(slope)

    return rt_diff, rt_ma, ma_slope


def get_target_price(tickers):
    target_list = []
    for ticker in tickers:
        price = pybithumb.get_current_price(ticker)
        target_price = price * 1.03
        target_list.append(target_price)
    return target_list


def data_transform(good_tickers):
    """
    데이터 프레임 형태로 각종 정보를 반환
    diff_ma5_curr : 5일간의 이동평균과 현재 가격의 차이
    ma5_list : 5일간의 이동평균 값 (손실을 막기 위한 하한가로 설정)
    ma_slope : 이동 평균간의 기울기
    target_price : 3% 이득을 가정한 목표가

    :return: 상기 정보가 포함되어 있는 데이터프레임
    """
    all_ticker = pybithumb.get_tickers()
    if good_tickers is None:
        good_tickers = check_bull_ticker(all_ticker)
    #good_tickers = ['ETC', 'QTUM', 'BTG', 'OMG', 'THETA', 'MXC', 'BEL', 'BCD', 'BCHA']
    need_col = ['closing_price', 'fluctate_rate_24H']

    # 5일 이동 평균과 현재가의 차이, 이동평균이 저장된 리스트, 이동평균의 기울기
    diff_ma5_curr, ma5_list, ma_slope = diff_ma_curr(good_tickers, 5)
    target_price = get_target_price(good_tickers)

    data = pybithumb.get_current_price("ALL")
    data = pd.DataFrame(data, index=need_col, columns=good_tickers).transpose()
    data['diff_rate_ma5'] = diff_ma5_curr
    data['target_price'] = target_price
    data['minimum_price'] = ma5_list
    data['ma_slope'] = ma_slope
    data = data.astype(float).round(decimals=2).sort_values(by=['ma_slope'], axis=0)

    return data


def get_left_krw(bithumb, commission):
    """
    잔고 확인 함수
    :return: 잔고, 정수형 반환
    """
    krw = int(bithumb.get_balance("BTC")[2])
    krw = int(krw - krw * commission)
    return krw


def maximum_units(ticker, balance):
    """
    해당 ticker에 대해 내 잔고로 구매할 수 있는 최대 개수 및 최우선 매도호가
    :param ticker: 가상화폐 이름
    :param balance: 내 통장 잔고
    :return: 최대 개수, 최우선 매도호가
    """
    orderbook = pybithumb.get_orderbook(ticker)
    sell_price = orderbook['asks'][0]['price']
    unit = balance / sell_price

    return unit, sell_price


def get_midtime(now):
    mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
    return mid


def check_balance(bithumb, tickers):
    for ticker in tickers:
        idx = tickers.index(ticker)
        length = len(tickers)
        rate = int((idx + 1) * 100 / length)
        os.system("cls")
        print("보유 자산 전체 매도 중... ", rate, "%")
        balance = bithumb.get_balance(ticker)[0]
        if balance > 0:
            try:
                bithumb.sell_market_order(ticker, balance)
                # print(ticker, " : ", balance, " 매도 완료")
            except:
                print("")
                # print(ticker, " : ", balance, " 매도 실패")


def wait_order(bithumb, order):
    flag = 0
    order_data = bithumb.get_order_completed(order)
    while order_data['data']['order_status'] != 'Completed':
        if flag > 12:
            if bithumb.cancel_order(order) == True:
                return -1
            else:
                return 0
        time.sleep(5)
        os.system("cls")
        print("매수 주문이 체결되기를 기다리는 중...")
        order_data = bithumb.get_order_completed(order)
        flag += 1
    return 0

# 틱차트 구현할 수 있다면 참 좋을텐데...
def check_bollinger_band(ticker):
    """
    mbb = 중심선 = 주가의 20시간 이동평균선
    ubb = 상한선 = 중심선 + 주가의 20시간 표준편차 * 2
    lbb = 하한선 = 중심선 - 주가의 20시간 표준편차 * 2
    perb = %b(현재 주가가 어디 위치에 있는지) = (주가 - 하한선) / (상한선 - 하한선)
    bw = 밴드폭 = (상한선 - 하한선) / 중심선
    bol_range = 기간(단위 시간)

    :param ticker: 단일 티커
    :return:
    """
    bol_range = 20
    data = pybithumb.get_candlestick(ticker, chart_intervals="1h")
    mbb = data.loc[:bol_range]['open'].mean()
    print(mbb)


def available_tickers(bithumb, tickers, sum_div):
    avail_tickers = []
    unvail_tickers = []
    tot = bithumb.get_balance("BTC")[2]
    tot = int(tot / sum_div)
    length = len(tickers)
    for ticker in tickers:
        idx = tickers.index(ticker)
        rate = int(((idx+1) * 100) / length)
        os.system("cls")
        print("Checking Available Tickers...", rate, "%")
        price = pybithumb.get_current_price(ticker)
        if price * 0.001 < tot:
            avail_tickers.append(ticker)
        else:
            unvail_tickers.append(ticker)

    return avail_tickers, unvail_tickers


def get_up_lower_div(poss_ticker, sum_div):

    tickers = list(poss_ticker.keys())
    up_div = 0
    low_div = 0
    need_tickers = 0
    if len(tickers) != 0:
        for ticker in tickers:
            if poss_ticker[ticker]['state'] == "upper":
                up_div += 1
            else:
                low_div += 1

        need_tickers = sum_div - (up_div + low_div)
        if need_tickers == 0:
            up_div = 0
            low_div = 0
        else:
            if need_tickers % 2 == 0:
                up_div = int(need_tickers / 2)
                low_div = int(need_tickers / 2)
            else:
                need_tickers += 1
                up_div = int(need_tickers / 2)
                low_div = int(need_tickers / 2)
                low_div -= 1
        return up_div, low_div

    else:
        up_div = 2
        low_div = 1
        return up_div, low_div





























