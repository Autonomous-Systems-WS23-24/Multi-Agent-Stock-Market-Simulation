import talib as tl

def strategy1(stockdata,risk_factor,money,stock_count):
    n=1
    # The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements.
    # It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
    stockdata["RSI"] = tl.RSI(stockdata['Close'], timeperiod=14)
    price_low = stockdata.at[stockdata.index[-1], 'Low']
    price_high = stockdata.at[stockdata.index[-1], 'High']
    price_mean = (price_low + price_high) / 2
    # moving average of last 52 days
    stockdata["MA"] = tl.MA(stockdata['Close'], timeperiod=26, matype=0)
    sell_price = 9999999999
    buy_price = 0
    # buying when RSI value is lower than 35, and the mean price is 5 euro lower than the MA52. Buy the stock for the mean price
    if stockdata.at[stockdata.index[-1],"RSI"] < 35 and price_mean <= (stockdata.at[stockdata.index[-1],"MA"] - 5/risk_factor) and money >= price_mean - 5 :
        buy_price = price_mean - 5
        if money > 5 * buy_price:
            n = 5
    # selling when RSI value is higher than 40 or if the low price is 5 lower than MA52. Sell the stock for the mean price
    elif stockdata.at[stockdata.index[-1],"RSI"] > 40 or price_low <= (stockdata.at[stockdata.index[-1],"MA"] - 5/risk_factor) and stock_count>0:
        sell_price = price_mean
        if stock_count>=5:
            n=5
    #print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')
    return buy_price, sell_price, n



def strategy2(stockdata,risk_factor,money,stock_count):
    n=1
    price_low = stockdata.at[stockdata.index[-1], 'Low']
    price_high = stockdata.at[stockdata.index[-1], 'High']
    price_mean = (price_low + price_high) / 2
    # moving average of last 52 days
    sma_period = 25
    stockdata["SMA"] = tl.MA(stockdata['Close'], timeperiod=sma_period, matype=0)
    buy_price = 0
    sell_price= 999999
    # Calculate a simple moving average (SMA) over the last N periods.
    #Buying if the mean is higher than the sma
    if price_mean*risk_factor < stockdata.at[stockdata.index[-1],"SMA"] and money >= price_mean:
        buy_price = price_mean
        if money > 5 * buy_price:
            n = 5
    #Selling if the mean is lower than the sma
    elif price_mean*risk_factor > stockdata.at[stockdata.index[-1],"SMA"] and stock_count>0:
        sell_price = price_mean
        if stock_count >= 5:
            n = 5
    #print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')
    return buy_price, sell_price, n




def strategy3(stockdata,risk_factor,money,stock_count):
    n=1
    # Define the period for Bollinger Bands calculation and the number of standard deviations
    bb_period = 20
    num_std_dev = 2

    # Calculate the rolling mean and standard deviation of the closing prices, 
    stockdata['RollingMean'] = stockdata['Close'].rolling(bb_period).mean()
    stockdata['RollingStd'] = stockdata['Close'].rolling(bb_period).std()

    # Calculate the upper and lower Bollinger Bands
    stockdata['UpperBand'] = stockdata['RollingMean'] + (num_std_dev * stockdata['RollingStd'])
    stockdata['LowerBand'] = stockdata['RollingMean'] - (num_std_dev * stockdata['RollingStd'])

    # Determine the buy and sell signals based on Bollinger Bands
    buy_price = 0
    sell_price = 9999999999

    if stockdata.at[stockdata.index[-1], 'Close'] < stockdata.at[stockdata.index[-1], 'LowerBand']*risk_factor and money >= stockdata.at[stockdata.index[-1], 'Close']:
        buy_price = stockdata.at[stockdata.index[-1], 'Close']
        if money > 5 * buy_price:
            n = 5
    elif stockdata.at[stockdata.index[-1], 'Close'] > stockdata.at[stockdata.index[-1], 'UpperBand']*risk_factor and stock_count>0:
        sell_price = stockdata.at[stockdata.index[-1], 'Close']*1.1
        if stock_count >= 5:
            n = 5

    #print(f'Upper Bollinger Band: {dataframe_stockdata.at[dataframe_stockdata.index[-1], "UpperBand"]:.2f}')
    #print(f'Lower Bollinger Band: {dataframe_stockdata.at[dataframe_stockdata.index[-1], "LowerBand"]:.2f}')
    #print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')

    return buy_price, sell_price, n


def strategy4(stockdata,risk_factor,money,stock_count):
    n=1
    # Define the short-term and long-term periods for the EMA calculation
    short_term_period = 12
    long_term_period = 26

    # Calculate the short-term and long-term exponential moving averages (EMA)
    short_term_ema = stockdata['Close'].ewm(span=short_term_period, adjust=False).mean()
    long_term_ema = stockdata['Close'].ewm(span=long_term_period, adjust=False).mean()

    # Calculate the MACD line by subtracting the long-term EMA from the short-term EMA
    macd_line = short_term_ema - long_term_ema

    # Define the signal line period
    signal_line_period = 9

    # Calculate the signal line as a 9-period EMA of the MACD line
    signal_line = macd_line.ewm(span=signal_line_period, adjust=False).mean()

    # Determine the buy and sell signals based on MACD
    buy_price = 0
    sell_price = 9999999999

    if macd_line.iloc[-1]*risk_factor > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]*risk_factor and money >= stockdata.at[stockdata.index[-1], 'Close']:
        buy_price = stockdata.at[stockdata.index[-1], 'Close']
        n=1
        if money> 5*buy_price:
            n = 5
    elif macd_line.iloc[-1]*risk_factor < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2]*risk_factor and stock_count>0:
        sell_price = stockdata.at[stockdata.index[-1], 'Close']
        if stock_count >= 5:
            n = 5

   # print(f'MACD Line: {macd_line.iloc[-1]:.2f}')
    #print(f'Signal Line: {signal_line.iloc[-1]:.2f}')
    #print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')

    return buy_price, sell_price, n



def stock_cue_calc(stock_data):
    # Calculate 52-day moving average
    stock_data['52-day MA'] = tl.MA(stock_data['Close'], timeperiod=52, matype=0)
    # Calculate 26-day moving average
    stock_data['26-day MA'] = tl.MA(stock_data['Close'], timeperiod=26, matype=0)
    # Calculate Relative Strength Index (RSI)
    stock_data['RSI'] = tl.RSI(stock_data['Close'], timeperiod=14)
    # Calculate Market Index and its slope
    stock_data['Market Index'] = (stock_data['High'] + stock_data['Low']) / 2
    stock_data['Market Index Slope'] = np.gradient(stock_data['Market Index'])
    # Calculate Market Level - Index Average
    market_index_average = stock_data['Market Index'].mean()
    stock_data['Market Level - Index Average'] = market_index_average
    # Calculate Market Index Acceleration
    stock_data['Market Index Acceleration'] = np.gradient(stock_data['Market Index Slope'])
    # Calculate MACD
    stock_data['MACD'], stock_data['Signal'], _ = tl.MACD(stock_data['Close'], fastperiod=12, slowperiod=26,
                                                          signalperiod=9)
    # Calcuate Stochastic Oscillator
    stock_data['K'], stock_data['D'] = tl.STOCH(stock_data['High'], stock_data['Low'], stock_data['Close'],
                                                fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3,
                                                slowd_matype=0)
    return stock_data

