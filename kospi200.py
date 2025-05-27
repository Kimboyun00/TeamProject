from data_loader import PykrxDataLoader
import pandas as pd
from pykrx import stock
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 코스피200 클래스 정의
class Kospi200DataLoader:
    def __init__(self, start_year: str, end_year: str):
        self.start_year = start_year
        self.end_year = end_year
    
    def get_next_trading_day(date):
        """
        입력 날짜가 휴장일이면 다음 영업일까지 반복해서 이동
        date: 'YYYYMMDD' 문자열
        """
        while True:
            # 삼성전자(005930)의 OHLCV 데이터 확인
            df = stock.get_market_ohlcv_by_date(date, date, "005930")
            if not df.empty:
                return date
            # 휴장일이면 다음날로 이동
            dt = datetime.strptime(date, "%Y%m%d") + timedelta(days=1)
            date = dt.strftime("%Y%m%d")

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

    def get_market_caps(self, codes):
        records = []
        for year in range(self.start_year-1, self.end_year+1):
            date = f"{year}0401"
            trading_date = Kospi200DataLoader.get_next_trading_day(date)
            cap_df = stock.get_market_cap_by_ticker(trading_date)
            for code in codes["주식코드"]:
                if code in cap_df.index:
                    market_cap = cap_df.loc[code, '시가총액']
                    records.append({
                        '주식코드': code,
                        '연도': year,
                        '날짜': trading_date,
                        '시가총액': market_cap
                    })
                else:
                    records.append({
                        '주식코드': code,
                        '연도': year,
                        '날짜': trading_date,
                        '시가총액': None
                    })
        df = pd.DataFrame(records)
        df = df.sort_values(by=['주식코드', '연도']).reset_index(drop=True)
        # 변화율(%) 계산
        df['시총변화율'] = df.groupby('주식코드')['시가총액'].pct_change()

        # # 변화량(절대값) 계산
        # df['시총변화량'] = df.groupby('주식코드')['시가총액'].diff()
        # 2015년부터의 데이터만 필터링
        df_filtered = df[df['연도'] >= 2015].reset_index(drop=True)
        return df_filtered





    
    # 종목 리스트의 수익률 데이터프레임 반환
    def kospi200_rtn(self, codes):
        records = []

        for code in codes['주식코드']:
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
    
    