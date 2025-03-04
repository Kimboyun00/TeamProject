# 거래 클래스 정의
# id: 주문 ID , dt: 날짜 , ticker: 거래 종목의 종목 코드 , amount: 거래 수량(절대값) , price: 거래 가격,
# direction: 거래 방향 , commission_rate: 거래 수수료 비율 , commission: 거래 수수료(자동 계산) , settlement: 정산 금액(자동 계산)

import datetime

import simulation.config as config
from simulation.order import OrderDirection

class Transaction(object):
    def __init__(self, id: str, dt: datetime.date, ticker: str, amount: int,
                 price: float, direction: OrderDirection,
                 commission_rate: float = config.commission_rate) -> None:
        self.id = id
        self.dt = dt
        self.ticker = ticker
        self.amount = amount
        self.price = price
        self.direction = direction
        self.commission_rate = commission_rate

        self.commission = (self.amount * self.price) * self.commission_rate
        self.settlement_value = -self.direction.value * (self.amount * self.price
                                                         ) - self.commission
            
# 수수료는 거래금액의 일정 비율로 계산된다.
# 세금과 기타 비용은 고려하지 않는다.