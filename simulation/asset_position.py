# 자산 포지션
# 자산 포지션은 투자자가 보유하고 있는 특정 자산에 대한 보유 상태나 보유량을 말한다.
# ticker: 종목 코드 , position: 보유 수량 , latest_price: 최신가격 , cost: 평균 초기 가격 , total_settlement_value: 모든 거래의 총 정산금액

from simulation.transaction import Transaction

# 자산 포지션 클래스 정의
class AssetPosition(object):
    def __init__(self, ticker: str, position: int, latest_price: float, cost: float):
        self.ticker = ticker
        self.position = position
        self.latest = latest_price
        self.cost = cost

        self.total_settlement_value = (-1.0) * self.position *self.cost

    # 자산포지션 클래스의 update() 메서드 정의
    # update() 메서드는 자산의 상태를 업데이트하는 메서드로 거래(transaction)를 입력받아서 자산의 총 정산 금액(total_settlement_value), 보유 수량(position), 평균 초기 가격(cost)을 업데이트함 
    def update(self, transaction: Transaction):
        self.total_settlement_value += transaction.settlement_value
        self.position += transaction.direction.value * transaction.amount
        self.cost = (-1.0) * self. total_settlement_value / self.position \
            if self.position != 0 else 0.0