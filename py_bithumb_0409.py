import pybithumb
import time
import vbtactic
import basicfunc
import datetime
import pandas as pd
import bollinger
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

order_list = []
danger_ticker = []
order_fail = 0 # 0이면 평소 상태, 1이면 매수 실패
while True:
    try:
        #매수 함수
        while not buy:
            if order_fail == 0:
                basicfunc.check_balance(bithumb, all_tickers)
                good_upper_tickers, good_lower_tickers = bollinger.check_safety(all_tickers, "buy")
                #complement_upper = list(set(good_upper_tickers).difference(danger_ticker)) 상한을 뚫는 상승장에 유리한 방법
                complement_lower = list(set(good_lower_tickers).difference(danger_ticker))
                #good_upper_tickers, diff_upper = vbtactic.recommend_ticker(complement_upper) 마찬가지.
                good_lower_tickers, diff_lower = vbtactic.recommend_ticker(complement_lower, "lower")

                good_tickers = good_lower_tickers
                diff = diff_lower

            elif order_fail == 1:
                good_tickers, diff = vbtactic.recommend_ticker(good_tickers, "lower")

            if len(good_tickers) != 0:
                data = {'diff': diff}
                df = pd.DataFrame(data=data, index=good_tickers).round(decimals=2).sort_values(by=['diff'], axis=0,
                                                                                               ascending=False)
                print(df)
                ticker = df.index[-1]
                order = vbtactic.buy_crypto_currency(bithumb, ticker)
                # print(order)
                order_data = bithumb.get_order_completed(order)
                if basicfunc.wait_order(bithumb, order) == -1:
                    order_fail = 1
                    raise Exception('그새 올랐네요.')

                # print(order_data)
                order_data = bithumb.get_order_completed(order)
                order = vbtactic.OrderList(order_data['data'])
                order_list.append(order)
                order_price = int(order_data['data']['order_price'])
                # print(order_data['data'])
                # print("체결가격: ", order_price)
                buy = True
                try:
                    danger_ticker.remove(ticker)
                except:
                    danger_ticker = []

            else:
                print("괜찮은 가상화폐가 없네요. 5분 후 재탐색 합니다.")
                ticker = None
                time.sleep(300)

        # 매도 함수
        if buy:

            now = datetime.datetime.now()
            mid = basicfunc.get_midtime(now)
            target_price = int(order_price * basicfunc.alpha)
            total = bithumb.get_balance("BTC")[2]
            while buy:
                try:
                    current_price = pybithumb.get_current_price(ticker)
                    now = datetime.datetime.now()
                    # pyautogui.hotkey('ctrl', 'u')
                    #os.system("cls")
                    print("<Crypto Currency Auto Trade Manager>")
                    print("-------------------------------------------------------\n")
                    print("현재 시각 : ", datetime.datetime.now())
                    print("보유 현금 : ", total)
                    print("감시 중인 Ticker: ", ticker, "목표 가격: ", target_price)
                    print("현재 가격: ", current_price)
                    print("매수 / 매도 주문 현황")
                    for status in order_list:
                        status.print_order()
                    print("\n-------------------------------------------------------")
                    tickers = [ticker]

                    if (current_price >= target_price) and (bollinger.check_safety(tickers, "sell") == 1):
                        order = vbtactic.sell_crypto_currency(bithumb, ticker)
                        if basicfunc.wait_order(bithumb, order) == -1:
                            raise Exception('그새 내렸네요.')
                        order_data = bithumb.get_order_completed(order)

                        print("이익 실현 / 매도 완료")
                        print(order)
                        print("\n-------------------------------------------------------")

                        order = vbtactic.OrderList(order_data['data'])
                        order_list.append(order)
                        total = bithumb.get_balance("BTC")[2]
                        ticker = None
                        buy = False

                    if current_price <= order_price * 0.90:
                        order = vbtactic.sell_crypto_currency(bithumb, ticker)
                        if basicfunc.wait_order(bithumb, order) == -1:
                            raise Exception('그새 내렸네요.')
                        order_data = bithumb.get_order_completed(order)

                        print("손실 확정 / 매도 완료")
                        print(order)
                        print("\n-------------------------------------------------------")
                        order = vbtactic.OrderList(order_data['data'])
                        order_list.append(order)
                        danger_ticker.append(ticker)
                        total = bithumb.get_balance("BTC")[2]

                        ticker = None
                        buy = False

                    if mid < now < mid + datetime.timedelta(seconds=10):
                        mid = basicfunc.get_midtime(now)
                        order = vbtactic.sell_crypto_currency(bithumb, ticker)
                        if basicfunc.wait_order(bithumb, order) == -1:
                            raise Exception('그새 내렸네요.')
                        basicfunc.check_balance(bithumb, all_tickers)
                        order_data = bithumb.get_order_completed(order)

                        print("자정 매도 완료")
                        print(order)
                        print("\n-------------------------------------------------------")
                        order = vbtactic.OrderList(order_data['data'])
                        order_list.append(order)
                        total = bithumb.get_balance("BTC")[2]

                        ticker = None
                        buy = False

                except:
                    print("")

                time.sleep(10)
    except:
        print("광범위한 오류")

























