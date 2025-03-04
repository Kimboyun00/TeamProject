# 계좌 클래스
# initial_cash: 초기 자금 , current_cash: 현재 자금 , dt: 날짜 ,Portfolio: 투자 포트폴리오 , orders: 현재 주문 목록
# transaction_history: 거래 히스토리 , portfolio_history: 투자 포트폴리오 히스토리 , account_history: 장부 금액 히스토리
# order_history: 주문 히스토리 , total_asset: 총 자산

from typing import List, Dict
import datetime
import pandas as pd

from simulation.transaction import Transaction
from simulation.order import Order, OrderStatus
from simulation.asset_position import AssetPosition

class Account(object):
    def __init__(self, initial_cash: float) -> None:
        self.initial_cash = initial_cash
        self.current_cash = initial_cash

        self.dt = None

        self.portfolio: Dict[str, AssetPosition] = {}
        self.orders: List[Order] = []

        self.transaction_history: List[Dict] = []
        self.portfolio_history: List[Dict] = []
        self.account_history: List[Dict] = []
        self.order_history: List[Dict] = []
        self.weight_asset: List[Dict] = initial_cash

    @property
    def total_asset(self) -> float:
        # 현재 총 자산 계산
        market_value = 0
        for asset_position in self.portfolio.values():
            market_value += asset_position.latest_price * asset_position.position
        return market_value + self.current_cash
    
    # 자산 포트폴리오 업데이트
    # update_position() 메서드
    # 거래가 발생했을 때 계좌를 업데이트 하기 위한 용도로 투자 포트폴리오 내 자산 포지션, 현재 현금, 거래 히스토리를 업데이트

    def update_position(self, transactions: Transaction):
        for tran in transactions:
            asset_exists = tran.ticker in self.portfolio.keys()
            if asset_exists:
                # 기존에 보유 중인 자산 포지션 업데이트
                self. portfolio[tran.ticker].update(transaction=tran)
            else:
                # 처음 보유하는 자산 추가
                new_position = AssetPosition(
                    ticker=tran.ticker, position=tran.direction.value*tran.amount,
                    latest_price=tran.price,
                    cost=abs(tran.settlement_value)/tran.amount
                )
                self.portfolio[tran.ticker] =new_position
            # 현재 현금 업데이트
            self.current_cash += tran.settlement_value
            # 거래 히스토리 업데이트
            self.settlement_history.append(vars(tran))

        # 투자 포트폴리오 업데이트
    # update_portfolio() 메서드
    # 주기적으로 포트폴리오의 자산을 평가하기 위한 용도로 투자 포트폴리오 내 자산가격, 투자 포트폴리오 히스토리, 장부금액 히스토리를 업데이트

    def update_portfolio(self, dt: datetime.date, data: pd.DataFrame):
        # 가격 데이터를 {종목 코드: OHLCV} 딕셔너리로 변환
        data = data.set_index('ticker').to_dict(orient='index')

        # 투자 포트폴리오 내 자산의 최신 가격(latest_price)을 업데이트
        for asset_position in self.portfolio.values():
            assert asset_position.ticker in data.keys()
            asset_position.latest_price = data[asset_position.ticker]['close']

            # 투자 포트폴리오 히스토리 업데이트 (현금과 자산)
            self.portfolio_history.append(
                {'date': dt, 'ticker': 'cash', 'latest_price': self.current_cash})
            self.portfolio_history.extend(
                [{'date': dt} | vars(asset_position)
                for asset_position in self.portfolio.values()])
            # 장부 금액 히스토리 업데이트
            self.account_history.append(
                {'date': dt, 'current_cash': self.current_cash,
                'total_asset': self.total_asset})
            
    # 주문 업데이트
    def update_order(self):
        # 완료 상태의 주문
        filled_orders = [order for order in self.orders
                        if order.status == OrderStatus.FILLED]
        # 주문 히스토리 업데이트
        self.order_history.extend([vars(order)for order in filled_orders])

        # 미완료 상태의 주문은 현재 주문으로 유지
        open_orders = [order for order in self.orders
                    if order.status == OrderStatus.OPEN]
        self.orders[:] = open_orders

        # 계좌에 있는 총자산(total_asset)을 읽는다.
        # 자산의 현재 가격(price)을 읽는다.
        # 총자산에 자산의 목표 편입 비중(target_percent)을 곱해서 목표 자산을 계산하고, 목표 자산을 현재가격으로 나눠서 목표 수량(target_amount)을 계산한다.

    def update_weight(self, dt: datetime.date, weight: dict):
        new_weight = weight.copy()
        new_weight['date'] = dt
        self.weight_history.append(new_weight)