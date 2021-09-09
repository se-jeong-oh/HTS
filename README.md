# HTS
Cryptocurrency Auto Trading Program

## Description
볼린저 매매 기법, 변동성 돌파전략과 이동평균을 이용해 적절한 종목을 찾아 자동으로 24시간 매매해주는 프로그램

## Prerequisite
Bithumb API를 이용하므로 Bithumb 계정이 필요 

## Files
* basicfunc.py
  * 프로그램을 실행하는데 필요한 기본적인 세팅과 함수 정의
  * Bithumb의 API를 활용하기 위한 함수
* bollinger.py
  * 볼린저 밴드를 구현하는데에 필요한 함수 정의
  * 볼린저 매매 기법에 의한 안전성 체크
* vbtactic.py
  * 변동성 돌파 전략을 구현하는데에 필요한 함수 정의
  * 종목들을 불러와 조건에 해당하는 종목코드를 찾고, 주문
* py_bithumb.py
  * 각 전략들을 종합하고 주문 여부 확인
  * 24시간 동작할 수 있도록 체크

## Usage
발급받은 Bithumb Key를 bithumb.txt로 만들어 같은 directory에 넣은 후 실행

## Update
- 2020.05 : Whipsaw 방어법을 찾을 때까지 잠정 연기
- 2020.04 : 더 정확한 예측을 위해 볼린저 밴드와 변동성 돌파전략 추가
- 2020.04 : 현재 자산 3등분 분산투자 기능 추가
- 2020.04 : 이동평균만을 이용해 매매시작
