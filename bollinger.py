import pybithumb
import os

suff = 1.01
whipsaw = 1.15

def check_bollinger_band(ticker):
    """
    mbb = 중심선 = 주가의 20시간 이동평균선
    ubb = 상한선 = 중심선 + 주가의 20시간 표준편차 * 2
    lbb = 하한선 = 중심선 - 주가의 20시간 표준편차 * 2
    perb = %b(현재 주가가 어디 위치에 있는지) = (주가 - 하한선) / (상한선 - 하한선)
    bw = 밴드폭 = (상한선 - 하한선) / 중심선
    bol_range = 기간(단위 시간)

    :param ticker: 단일 티커
    :return: ( 20시간 이동평균선 , 상한선, 하한선, 현재 위치, 밴드폭 )
    """
    bol_dict = {}
    bw_list = []

    bol_range = -20
    length = 10
    list_calc = [0, 1, length]
    data = pybithumb.get_candlestick(ticker, chart_intervals="1h")

    for i in list_calc:
        start = -i
        end = start
        start = bol_range + start
        price_data = data.iloc[start:end-1]['open']
        mbb = price_data.mean()
        std_dev = int(price_data.std())
        ubb = mbb + std_dev * 2
        lbb = mbb - std_dev * 2

        bw = (ubb - lbb) / mbb
        bw_list.append(bw) # 최근부터 과거로 향하며 저장됨, 1시간 단위, 20시간 기간
        if i == 0:
            price = pybithumb.get_current_price(ticker)
            low_price = data.iloc[-1]['low']
            high_price = data.iloc[-1]['high']
            # -1 이면 위험

            if price >= low_price * whipsaw:
                bol_dict['whipsaw'] = -1
            elif price <= high_price * (2 - whipsaw):
                bol_dict['whipsaw'] = -1
            else:
                bol_dict['whipsaw'] = 1
            try:
                perb = (price - lbb) / (ubb - lbb)
            except:
                perb = 0
            bol_dict['mbb'] = mbb
            bol_dict['ubb'] = ubb
            bol_dict['lbb'] = lbb
            bol_dict['perb'] = perb
            bol_dict['bw'] = bw


    # 시작과 현재 기울기, 지금과 직전의 기울기
    avg_grd = abs((bw_list[0] - bw_list[-1]) / length)
    lim_grd = abs((bw_list[0] - bw_list[1]) / 1)
    if avg_grd < lim_grd:
        bol_dict['signal'] = 1 # 급격한 변화(오목)
    else:
        bol_dict['signal'] = -1 # 완만한 변화(볼록)

    return bol_dict


def check_safety(tickers, func):

    if func == "buy":
        good_upper_tickers = [] # 상승하는 ticker
        good_lower_tickers = [] # 최대 하락한 ticker

        for ticker in tickers:
            idx = tickers.index(ticker)
            rate = int((idx + 1) * 100 / len(tickers))
            os.system("cls")
            print("Finding Profitable Tickers (Bollinger Band)... ", rate, "%")
            data = check_bollinger_band(ticker)
            price = pybithumb.get_current_price(ticker)

            # 상한선을 뚫었을 때!
            if price * suff >= data['ubb']:
                if data['signal'] == 1 and data['whipsaw'] != -1:
                    good_upper_tickers.append(ticker)

            # 하한선에 근접했을 때!
            elif data['lbb'] * 0.99 < price < data['lbb'] * 1.01:
                if data['signal'] == 1 and data['whipsaw'] != -1:
                    good_lower_tickers.append(ticker)

        return good_upper_tickers, good_lower_tickers

    elif func == "sell":
        for ticker in tickers:
            data = check_bollinger_band(ticker)
            price = pybithumb.get_current_price(ticker)
            # 1을 리턴하면 매도하라는 뜻

            if price >= data['ubb']:
                if data['signal'] == -1 and data['whipsaw'] != -1:
                    return 1
            elif price <= data['lbb']:
                if data['signal'] == -1 and data['whipsaw'] != -1:
                    return 1
        return -1

