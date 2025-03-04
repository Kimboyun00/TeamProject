# 중개인
# 중개인의 주요 역할을 주문 체결로 국한하고 주문 체결 시마다 슬리피지를 계산한다.
# 슬리피지 가정 : 투자자에게 불리한 슬리피지만 존재한다.
#              주문 체결량은 총 거래량의 최대 10%를 넘지 않는다
#              슬리피지는 가격의 일정 비율로 발생한다.

# 중개인 클래스 속성
# slippage_rate: 슬리피지 비율 , volume_limit_rate: 거래량 제한 비율

from typing import List, Dict, Optional, Tuple
import datetime
import pandas as pd

import simulation.config as config
from simulation.order import Order, OrderStatus, OrderDirection
from simulation.transaction import Transaction

class Broker(object):
    def __init__(self , slippage_rate: float = config.slippage_rate,
                 volume_limit_rate: float = config.volume_limit_rate):
            self.slippage_rate = slippage_rate
            self.volume_limit_rate = volume_limit_rate

    # 슬리피지 계산

    def calculate_slippage(self, data = Dict, order = Order) -> Tuple[float, int]:
        # 슬리피지를 포함한 거래 가격 계산
        price = data['open']
        simulated_impact = price * self.slippage_rate

        # 거래 방향과 현재 가격을 기준으로 슬리피지를 포함한 거래 가격을 계산한다.
        # 매수인 경우 현재가격 + 슬리피지 , 매도인 경우 현재가격 - 슬리피지
        if order.direction == OrderDirection.BUY:
            impacted_price = price + simulated_impact
        else:
            impacted_price = price - simulated_impact

        # 최대 주문 비율(vloume_limit_rate)로 계산된 최대 주문량과 주문 수량 중 큰 값으로 최종 체결량을 계산한다.
        volume = data['volume']
        max_volume = volume * self.volume_limit_rate
        shares_to_fill = min(order.open_amount, max_volume)

        return impacted_price, shares_to_fill
    
    # 주문 처리

    def process_order(self, dt: datetime.date, data: pd.DataFrame,
                    orders: Optional[List[Order]]) -> List[Transaction]:
        if orders is None:
            return []
        
        # 가격 데이터를 딕셔너리로 변환
        data = data.set_index('ticker').to_dict(orient='index')

        transactions = []
        for order in orders:
            if order.status == OrderStatus.OPEN:
                assert order.ticker in data.keys()
                # 슬리피지 계산
                price, amount = self.calculate_slippage(
                    data=data[order.ticker],
                    order=order
                )
                if amount != 0:
                    # 거래 객체 생성
                    transaction = Transaction(
                        id=order.id,
                        dt=dt,
                        ticker=order.ticker,
                        amount=amount,
                        price=price,
                        direction=order.direction,
                    )
                    transactions.append(transaction)
                    # 거래 객체의 상태와 미체결 수량 업데이트
                    if order.open_amount == transaction.amount:
                        order.status = OrderStatus.FILLED
                    order.open_amount -= transaction.amount

        return transactions