from data_loader import PykrxDataLoader
import pandas as pd
from pykrx import stock
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class Kospi200DataLoader:
    def __init__(self, start_year: str, end_year: str):
        self.start_year = start_year
        self.end_year = end_year
    
    # 지정한 기간동안의 코스피200 종목의 중복값 제외한 리스트 반환
    def kospi200_list(self):
        # 결과를 저장할 리스트 생성
        records = []

        for year in range(self.start_year, self.end_year + 1):
            date = f"{year}-12-31"  # 연말 기준 (휴장일일 경우 이전 영업입)
            df = stock.get_index_portfolio_deposit_file("1028", f"{year}1231", alternative = True)
            # 각 코드에 대해 연도와 함께 리스트에 저장
            for code in df:
                records.append({'연도': year, '주식코드': code})

        # 리스트를 데이터프레임으로 변환
        result_df = pd.DataFrame(records)

        frequency = result_df['주식코드'].value_counts()
        frequency_df = frequency.reset_index()
        frequency_df.columns = ['주식코드', '빈도수']
        code_df = frequency_df[['주식코드']]
        code_list = code_df['주식코드'].tolist()

        return code_list
    
    # 종목 리스트의 수익률 데이터프레임 반환
    def kospi200_rtn(self, df):
        records = []

        for code in df['주식코드']:
            df = stock.get_market_ohlcv_by_date(
                f"{self.start_year}0101", f"{self.end_year}1231", code, freq='y'
            )
            if not df.empty:
                df = df[['시가', '종가']].reset_index()  # 시가 포함
                df['연도'] = df['날짜'].dt.year
                # 시가 대비 종가 변화율 계산
                df['수익률'] = ((df['종가'] - df['시가']) / df['시가'])
                records.append(df.assign(주식코드=code))

        # Long-form 데이터 생성
        result_df = pd.concat(records)[['주식코드', '연도', '수익률']]

        # 1. 무한대 값을 NaN으로 변환
        result_df = result_df.replace([np.inf, -np.inf], np.nan) 
        result_df.dropna(inplace=True)

        return result_df
    
    