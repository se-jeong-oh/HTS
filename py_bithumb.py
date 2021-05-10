import pybithumb
import time
import vbtactic
import basicfunc
import datetime
import pandas as pd
import bollinger
import random
import pyautogui
import os
"""
Key	Description - get_current_price("ALL")
opening_price	최근 24시간 내 시작 거래금액
closing_price	최근 24시간 내 마지막 거래금액
min_price 최근	24시 간 내 최저 거래금액
max_price 최근	24시 간 내 최고 거래금액
average_price	최근 24시간 내 평균 거래금액
units_traded	최근 24시간 내 Currency 거래량
volume_1day	최근 1일간 Currency 거래량
volume_7day	최근 7일간 Currency 거래량
buy_price	거래 대기건 최고 구매가
sell_price	거래 대기건 최소 판매가
24H_fluctate	24시간 변동금액
24H_fluctate_rate	24시간 변동률

CK : cf1df2b779eab95116301c4eb31f40cc
SK : d983ab8f5f5762c4ecd3ca689fa9054c


"""
"""
pybithumb 함수 설명
-------------------------------------------------------------
###func buy_limit_order###

    input arg : 가상화폐의 티커, 지정가(정수형 주의), 매수 수량
    return res : 주문 종류(bid, ask), 가상화폐 티커, 주문번호

    order = bithumb.buy_limit_order(ticker, price, unit)

-------------------------------------------------------------

-------------------------------------------------------------

"""
"""
if ticker is not None and func is not None:
    krw = basicfunc.get_left_krw(bithumb, basicfunc.commission)
    print(pybithumb.get_current_price(ticker))
    if func == "Buy":
        unit, price = basicfunc.maximum_units(ticker, krw)
        order = bithumb.buy_limit_order(ticker, price, unit)
        data = basicfunc.data_transform([ticker])
        print(order)
        print("target_price : ", data['target_price'])

    elif func == "Sell":
        unit = bithumb.get_balance(ticker)[0]
        print(unit)

        order = bithumb.sell_market_order(ticker, unit)
        # order = bithumb.sell_limit_order(ticker, 4000000, unit)
        print(order)

        if cancel:
            time.sleep(10)
            cancel = bithumb.cancel_order(order)
            print(cancel)

elif func == "data":
    data = basicfunc.data_transform(None)
    print(data)
"""

all_tickers = pybithumb.get_tickers()
basicfunc.basic_setting()
bithumb = basicfunc.bithumb_set()

ticker = None
buy = False
# 상승주 비율
up_rate = 0.7
# 총 종목의 수
sum_div = 3
# 현재 보유 종목 수
curr_up_ticker = 0
curr_low_ticker = 0
curr_ticker = curr_up_ticker + curr_low_ticker

poss_ticker = {}
poss_keys = ['state', 'order_price', 'price', 'target_price']

order_list = []
danger_ticker = []
buy_list = []
order_fail = 0 # 0이면 평소 상태, 1이면 매수 실패
flag = 1
while flag == 1:
    try:
        basicfunc.check_balance(bithumb, all_tickers)
        flag = 0
    except:
        flag = 1
all_tickers = pybithumb.get_tickers()
all_tickers, unvail_tickers = basicfunc.available_tickers(bithumb, all_tickers, sum_div)
while True:
    try:
        # 매수 함수
        curr_ticker = len(list(poss_ticker.keys()))

        # up_div = int(sum_div * up_rate)
        # low_div = sum_div - up_div

        while (len(list(poss_ticker.keys())) < 3) and bithumb.get_balance("BTC")[2] > 1000:
            good_tickers = []
            diff = []
            all_tickers = pybithumb.get_tickers()
            all_tickers = list(set(all_tickers).difference(unvail_tickers))

            if order_fail == 1:
                tmp_ticker_list = list(poss_ticker.keys())
                for tickerr in tmp_ticker_list:
                    try:
                        all_tickers.remove(tickerr)
                    except:
                        pass
                order_fail = 0

            good_upper_tickers, good_lower_tickers = bollinger.check_safety(all_tickers, "buy")
            complement_upper = list(set(good_upper_tickers).difference(danger_ticker))
            complement_lower = list(set(good_lower_tickers).difference(danger_ticker))

            good_upper_tickers, diff_upper = vbtactic.recommend_ticker(complement_upper, "upper")
            good_lower_tickers, diff_lower = vbtactic.recommend_ticker(complement_lower, "lower")

            # good_upper_tickers = ['BCH', 'BTG']
            # diff_upper = [0.01, 0.01]
            # good_lower_tickers = ['ANKR']
            # diff_lower = [0.01]

            length_up = len(good_upper_tickers)
            length_low = len(good_lower_tickers)

            data = {'diff': diff_upper}
            df_up = pd.DataFrame(data=data, index=good_upper_tickers).round(decimals=2).sort_values(by=['diff'], axis=0, ascending=False)
            data = {'diff': diff_lower}
            df_low = pd.DataFrame(data=data, index=good_lower_tickers).round(decimals=2).sort_values(by=['diff'], axis=0, ascending=False)

            """
            이 부분은 나중에 수정해야함
            """
            good_upper_tickers = df_up.index
            diff_upper = df_up['diff']
            good_lower_tickers = df_low.index
            diff_lower = df_low['diff']

            curr_ticker = len(list(poss_ticker.keys()))
            need_ticks = sum_div - curr_ticker
            up_div, low_div = basicfunc.get_up_lower_div(poss_ticker, sum_div)

            # 추천된 ticker의 개수가 내가 분산하고자 하는 종목의 수보다 많다면
            if (length_up + length_low) >= need_ticks:
                if length_up < up_div:
                    up_div = length_up
                    low_div = need_ticks - up_div
                elif length_low < low_div:
                    low_div = length_low
                    up_div = need_ticks - low_div

            # 추천된 ticker의 개수가 내가 분산하고자 하는 종목의 수보다 적다면
            elif 0 < (length_up + length_low) < need_ticks:
                up_div = length_up
                low_div = length_low

            # 추천된 ticker의 개수가 아예 없다면.
            else:
                print("괜찮은 가상화폐가 없네요. 5분 후 재탐색 합니다.")
                time.sleep(300)
                raise Exception("가상화폐 발견 실패")

            try:
                for i in range(up_div):
                    # -1, 리스트 가장 끝에 있는 ticker가 0.0 으로 이제 막 뚫기 시작했다.
                    index = (-i)-1
                    ticker = good_upper_tickers[index]
                    good_tickers.append(ticker)
                    diff.append(diff_upper[index])
                    poss_ticker[ticker] = dict.fromkeys(poss_keys)

                    poss_ticker[ticker]['state'] = "upper"
            except:
                print("상승장 종목 오류, 179 lines")

            try:
                for i in range(low_div):
                    index = (-i)-1
                    ticker = good_lower_tickers[index]
                    good_tickers.append(ticker)
                    diff.append(diff_lower[index])
                    poss_ticker[ticker] = dict.fromkeys(poss_keys)
                    poss_ticker[ticker]['state'] = "lower"

            except:
                print("하락장 종목 오류, 190 lines")

            # 밑에서부터 good_tickers에 있는 ticker 들을 매수
            if len(good_tickers) != 0:
                data = {'diff': diff}
                df = pd.DataFrame(data=data, index=good_tickers).round(decimals=2).sort_values(by=['diff'], axis=0,
                                                                                               ascending=False)
                print(df)

                good_tickers.reverse()
                # ticker = df.index[-1]
                for ticker in good_tickers:
                    order = vbtactic.buy_crypto_currency(bithumb, ticker, sum_div, curr_ticker)
                    # print(order)
                    print(ticker, "주문 시작")
                    if basicfunc.wait_order(bithumb, order) == -1:
                        print(ticker, "주문 취소")
                        order_fail = 1
                        del poss_ticker[ticker]
                        continue
                    print(ticker, "주문 완료!")
                    try:
                        order_data = bithumb.get_order_completed(order)
                        # time.sleep(1)
                        # order = vbtactic.OrderList(order_data['data'])
                        # order_list.append(order)
                        order_price = float(order_data['data']['order_price'])
                        poss_ticker[ticker]['order_price'] = order_price
                    except:
                        print("order 객체, poss_ticker 오류. 222 lines")
                    curr_ticker += 1

                    if poss_ticker[ticker]['state'] == "upper":
                        curr_up_ticker += 1
                        up_div -= 1
                    elif poss_ticker[ticker]['state'] == "lower":
                        curr_low_ticker += 1
                        low_div -= 1

                    # print(order_data['data'])
                    # print("체결가격: ", order_price)
                    buy = True



            else:
                print("괜찮은 가상화폐가 없네요. 5분 후 재탐색 합니다.")
                ticker = None
                time.sleep(300)

        buy = True

        try:
            danger_ticker.remove(ticker)
        except:
            danger_ticker = []
        # up_div = int(sum_div * up_rate)
        # low_div = sum_div - up_div

        # 매도 함수
        if buy:

            now = datetime.datetime.now()
            mid = basicfunc.get_midtime(now)

            ticker_list = list(poss_ticker.keys())
            curr_ticker = len(ticker_list)
            os.system("cls")
            while (bithumb.get_balance("BTC")[2] < 1000) and (len(list(poss_ticker.keys())) == sum_div):
                try:
                    curr_ticker = len(list(poss_ticker.keys()))
                    total = bithumb.get_balance("BTC")[2]

                    now = datetime.datetime.now()
                    # pyautogui.hotkey('ctrl', 'u')
                    os.system("cls")
                    print("\n-------------------------------------------------------")
                    print("<Crypto Currency Auto Trade Manager>")
                    print("-------------------------------------------------------\n")
                    print("현재 시각 : ", datetime.datetime.now())
                    print("총 보유 자산 : ", total)
                    print("\n-------------------------------------------------------\n")
                    for i in range(curr_ticker):
                        ticker = ticker_list[i]
                        order_price = poss_ticker[ticker]['order_price']
                        target_price = int(poss_ticker[ticker]['order_price'] * basicfunc.alpha)
                        current_price = pybithumb.get_current_price(ticker)
                        poss_ticker[ticker]['target_price'] = target_price
                        print("감시 중인 Ticker: ", ticker)
                        print("목표 가격: ", target_price)
                        print("현재 가격: ", current_price)
                        print("구매 가격:", order_price)
                        print("\n#############################\n")
                    # print("<매수 / 매도 주문 현황>")
                    # for status in order_list:
                    #     status.print_order()
                    for ticker in ticker_list:
                        tickers = [ticker]
                        current_price = pybithumb.get_current_price(ticker)
                        target_price = poss_ticker[ticker]['target_price']
                        order_price = poss_ticker[ticker]['order_price']
                        if (current_price >= target_price) or (bollinger.check_safety(tickers, "sell") == 1):
                            order = vbtactic.sell_crypto_currency(bithumb, ticker)
                            if basicfunc.wait_order(bithumb, order) == -1:
                                print(ticker, "가격이 그새 내려갔나봐요.")
                                continue
                            # order_data = bithumb.get_order_completed(order)
                            del poss_ticker[ticker]
                            print("이익 실현 / 매도 완료")
                            # print(order)
                            print("\n-------------------------------------------------------")
                            # try:
                            #     order = vbtactic.OrderList(order_data['data'])
                            #     order_list.append(order)
                            # except:
                            #     print(order_data)
                            #     print(order)
                            #     print("오류 발생, 313 lines")
                                # ticker = None
                                # buy = False

                        elif current_price <= order_price * 0.94:
                            order = vbtactic.sell_crypto_currency(bithumb, ticker)
                            if basicfunc.wait_order(bithumb, order) == -1:
                                print(ticker, "가격이 그새 내려갔나봐요.")
                                continue

                            # order_data = bithumb.get_order_completed(order)
                            del poss_ticker[ticker]
                            print("손실 확정 / 매도 완료")
                            # print(order)
                            print("\n-------------------------------------------------------")
                            # try:
                            #     order = vbtactic.OrderList(order_data['data'])
                            #     order_list.append(order)
                            # except:
                            #     print(order_data)
                            #     print(order)
                            #     print("오류 발생, 334 lines")

                            danger_ticker.append(ticker)

                            # ticker = None
                            # buy = False

                        # elif mid < now < mid + datetime.timedelta(minutes=10):
                        #     mid = basicfunc.get_midtime(now)
                        #     # order = vbtactic.sell_crypto_currency(bithumb, ticker)
                        #
                        #     # basicfunc.check_balance(bithumb, all_tickers)
                        #     while len(list(poss_ticker.keys())) != 0:
                        #         sell_tickers = list(poss_ticker.keys())
                        #         for sell_ticker in sell_tickers:
                        #             order = vbtactic.sell_crypto_currency(bithumb, sell_ticker)
                        #             if basicfunc.wait_order(bithumb, order) == -1:
                        #                 print(ticker, "가격이 그새 내려갔나봐요.")
                        #                 continue
                        #             # order_data = bithumb.get_order_completed(order)
                        #             del poss_ticker[ticker]
                        #             # try:
                        #             #     order = vbtactic.OrderList(order_data['data'])
                        #             #     order_list.append(order)
                        #             # except:
                        #             #     print(order_data)
                        #             #     print(order)
                        #             #     print("오류 발생, 359 lines")
                        #
                        #     print("자정 전량 매도 완료")
                        #     print("10분간 매매를 정지합니다.")
                        #     print("\n-------------------------------------------------------")
                        #     time.sleep(600)
                        #     break

                            # ticker = None
                            # buy = False

                    curr_ticker = len(list(poss_ticker.keys()))

                    time.sleep(1)


                except:
                    print("매도 주문 오류, line 357")

            print("추가 매수를 진행합니다.")

            time.sleep(10)
    except:
        print("광범위한 오류")

























