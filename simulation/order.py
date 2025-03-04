from typing import Optional
from enum import Enum
import datetime
import uuid

# 주문 (OrderType 클래스)
# MARKET: 시장가 주문 , LIMIT: 지정가 주문 , STOPMARKET: 정지 시장가 주문 , STOPLIMIT: 정지 지정가 주문
class OrderType(Enum):
    MARKET = 1
    LIMIT = 2
    STOPMARKET = 3
    STOPLIMIT = 4

# 주문 (OrderStatus 클래스)
# OPEN: 미체결(혹은 부분 체결) , FILLED: 체결 , CANCELED: 취소
class OrderStatus(Enum):
    OPEN = 1
    FILLED = 2
    CANCELED = 3

# 주문 (OrderDirection 클래스)
# BUY: 매수 , SELL: 매도
class OrderDirection(Enum):
    BUY = 1
    # 계산에 용이하게 사용하기 위해 -1 사용
    SELL = -1

# 주문 클래스 정의
# id: 주문 ID , dt: 날짜 , ticker: 거래 종목의 종목 코드 , amount: 주문 수량(절대값) , type: 주문 유형
# limit: 지정가 여부 , stop: 정지 주문 여부 , status: 주문 상태 , open_amount: 미체결 수량


class Order(object):
    def __init__(self, dt: datetime.date, ticker: str, amount: int,
                 type: Optional[OrderType] = OrderType.MARKET,
                 limit: Optional[float] = None, stop: Optional[float] = None,
                 id: Optional[str] = None) -> None:
        self.id = id if id is not None else uuid.uuid4().hex
        self.dt = dt
        self.ticker = ticker
        # amount변수는 부호가 있는 숫자로 표현되어 있어 주문수량(amount)이 양수이면 매수를 음수이면 매도를 나타냄
        self.amount = abs(amount)
        self.direction = OrderDirection.BUY if amount > 0 else OrderDirection.SELL
        self.type = type
        self.limit = limit
        self.stop = stop

        self.status: OrderStatus = OrderStatus.OPEN
        self.open_amount: int = self.amount