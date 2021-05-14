import time
import pyupbit
import datetime
import pandas as pd

access = "GgRPpycsO1XEaUVCMKOgiqo3KnKHgnkJZWdn86nd"          # 본인 값으로 변경
secret = "J4leeX9Bpt5PlWE6rVuXvtFPTV5u0LU5baTLrDfh"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

df = pyupbit.get_ohlcv("KRW-BTC",interval="minute15", count=200)

#변동성 돌파 전략으로 매수 목표가 조회
def get_target_price(ticker, k):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

#단순 이동 평균(Simple Moving Average, SMA)
def SMA(df, period=30, column="close"):
    return df[column].rolling(window=period).mean()

#지수 이동 평균(Exponential Moving Average, EMA)
def EMA(df, period=20, column="close"):
    return df[column].ewm(span=period, adjust=False).mean()

#이동 평균 수렴/발산 계산함수 MACD
def MACD(df, period_long=26, period_short=12, period_signal=9, column="close"):
    #단기 지수 이평선 계산(AKA Fast Moving Average)
    ShortEMA = EMA(df, period_short, column=column)

    #장기 지수 이평선 계산(AKA Slow Moving Average)
    LongEMA = EMA(df, period_long, column=column)

    #이동평균수렴/발산 계산
    df["MACD"] = ShortEMA - LongEMA
    
    #신호선 계산
    df["Signal_Line"] = EMA(df, period_signal, column="MACD")

    df["MACD_oscillator"]=df["MACD"]-df["Signal_Line"]

    return df

df=MACD(df,26,12,9)

#상대적 강도 지수 RSI

def RSI(df, period = 14, column="close"):
    delta = df[column].diff(1)
    delta = delta.dropna()

    up = delta.copy()
    down = delta.copy()

    up[up<0]=0
    down[down>0]=0

    df["up"]=up
    df["down"]=down

    AVG_Gain = SMA(df, period, column="up")
    AVG_Loss = abs((SMA(df, period, column="down")))
    RS=(AVG_Gain / AVG_Loss)

    RSI = 100.0 - (100.0/(1.0+RS))
    df["RSI"] = RSI

    return df

df = MACD(df, period_long=26, period_short=12, period_signal=9)
df = RSI(df, period=14)
df["SMA"] = SMA(df, period=30)
df["EMA"] = EMA(df, period=20)

# 볼린저 밴드
def bb(df):
    """
    Calculate Bollinger Bands
    ubb = MA_w(x) + k * sd(x)
    mbb = MA_w(x)
    lbb = MA_w(x) - k * sd(x)
    :param x:
    :return: (ubb, mbb, lbb)
    """
    df["ubb"] = SMA(df, period=20) + 2 * df["close"].rolling(20).std()
    df["mbb"] = SMA(df, period=20)
    df["lbb"] = SMA(df, period=20) - 2 * df["close"].rolling(20).std()
    # ubb.plot(x='Date', y='UBB')
    # mbb.plot(x='Date', y='MBB')
    # lbb.plot(x='Date', y='LBB')
    # plt.show()

    return df

df = bb(df)

# 시작 시간 조회
def get_start_time(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

# 15일 이동 평균선 조회
def get_ma15(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

# 잔고 조회
def get_balance(ticker): 
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

# 현재가 조회
def get_current_price(ticker):
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

i=1
while True:
    i+=1
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        #end_time = start_time + datetime.timedelta(days=1)
        print(now)
        ma15 = get_ma15("KRW-BTC")
        target_price = get_target_price("KRW-BTC", 0.5)
        current_price = get_current_price("KRW-BTC")

        if ma15 < current_price and target_price < current_price and df.iloc[i,7] < 0 and df.iloc[i,10]<32 and current_price<bb("lbb"):
            krw = get_balance("KRW")
            if krw > 5000:
                time.sleep(1800)
                if ma15 < current_price and target_price < current_price and df.iloc[i,7] < 0 and df.iloc[i,10]<32 and current_price<df.iloc[i,15]:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.25)
                    time.sleep(600)
                if ma15 < current_price and target_price < current_price and df.iloc[i,7] < 0 and df.iloc[i,10]<32 and current_price<df.iloc[i,15]:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.3333)
                    time.sleep(700)
                if ma15 < current_price and target_price < current_price and df.iloc[i,7] < 0 and df.iloc[i,10]<32 and current_price<df.iloc[i,15]:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.5)
                    time.sleep(700)
                if ma15 < current_price and target_price < current_price and df.iloc[i,7] < 0 and df.iloc[i,10]<32 and current_price<df.iloc[i,15]:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)
        
        elif ma15 > current_price and target_price > current_price and df.iloc[i,7] > 0 and df.iloc[i,10]>65 and current_price>df.iloc[i,13]:
            btc = get_balance("BTC")
            if btc > 0.00008:
                time.sleep(1800)
                if ma15 > current_price and target_price > current_price and df.iloc[i,7] > 0 and df.iloc[i,10]>65 and current_price>df.iloc[i,13]:
                    sell_result = upbit.sell_market_order("KRW-BTC", btc*0.25)
                    time.sleep(700)
                if ma15 > current_price and target_price > current_price and df.iloc[i,7] > 0 and df.iloc[i,10]>65 and current_price>df.iloc[i,13]:
                    sell_result = upbit.sell_market_order("KRW-BTC", btc*0.3333)
                    time.sleep(700)
                if ma15 > current_price and target_price > current_price and df.iloc[i,7] > 0 and df.iloc[i,10]>65 and current_price>df.iloc[i,13]:
                    sell_result = upbit.sell_market_order("KRW-BTC", btc*0.5)
                    time.sleep(700)
                if ma15 > current_price and target_price > current_price and df.iloc[i,7] > 0 and df.iloc[i,10]>65 and current_price>df.iloc[i,13]:
                    sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
        else:
            print("대기")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
