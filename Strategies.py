def strategy1(dataframe_stockdata,risk_factor,money,stock_count):
    # The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements.
    # It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
    RSI_value = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'RSI']
    price_low = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Low']
    price_high = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'High']
    price_mean = (price_low + price_high) / 2
    # moving average of last 52 days
    MA52 = dataframe_stockdata.at[dataframe_stockdata.index[-1], '52-day MA']
    #print(f'RSI: {RSI_value}', f'MA of alst 52 days: {MA52}')
    # buying when RSI value is lower than 35, and the mean price is 5 euro lower than the MA52. Buy the stock for the mean price
    if RSI_value < 35 and price_mean <= (MA52 - 5/risk_factor) and money >= price_mean - 5 :
        buy_price = price_mean - 5
    else:
        buy_price = 0
    # selling when RSI value is higher than 40 or if the low price is 5 lower than MA52. Sell the stock for the mean price
    if RSI_value > 40 or price_low <= (MA52 - 5/risk_factor) and stock_count>0:
        sell_price = price_mean
    else:
        sell_price = 9999999999
    #print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')
    return buy_price, sell_price



def strategy2(dataframe_stockdata,risk_factor,money,stock_count):
    price_low = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Low']
    price_high = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'High']
    price_mean = (price_low + price_high) / 2

    # Calculate a simple moving average (SMA) over the last N periods. 
    sma_period = 25
    sma = dataframe_stockdata["Close"][-sma_period:].mean()
    #print(f'SMA of last {sma_period} days: {sma} ')

    #Buying if the mean is higher than the sma
    if price_mean*risk_factor < sma and money >= price_mean :
        buy_price = price_mean 
    else:
        buy_price = 0
    #Selling if the mean is lower than the sma
    if price_mean*risk_factor > sma and stock_count>0:
        sell_price = price_mean
    else:
        sell_price = 9999999999
    #print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')
    return buy_price, sell_price




def strategy3(dataframe_stockdata,risk_factor,money,stock_count):
    # Define the period for Bollinger Bands calculation and the number of standard deviations
    bb_period = 20
    num_std_dev = 2

    # Calculate the rolling mean and standard deviation of the closing prices, 
    dataframe_stockdata['RollingMean'] = dataframe_stockdata['Close'].rolling(bb_period).mean()
    dataframe_stockdata['RollingStd'] = dataframe_stockdata['Close'].rolling(bb_period).std()

    # Calculate the upper and lower Bollinger Bands
    dataframe_stockdata['UpperBand'] = dataframe_stockdata['RollingMean'] + (num_std_dev * dataframe_stockdata['RollingStd'])
    dataframe_stockdata['LowerBand'] = dataframe_stockdata['RollingMean'] - (num_std_dev * dataframe_stockdata['RollingStd'])

    # Determine the buy and sell signals based on Bollinger Bands
    buy_price = 0
    sell_price = 9999999999

    if dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close'] < dataframe_stockdata.at[dataframe_stockdata.index[-1], 'LowerBand']*risk_factor and money >= dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close']:
        buy_price = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close']
    elif dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close'] > dataframe_stockdata.at[dataframe_stockdata.index[-1], 'UpperBand']*risk_factor and stock_count>0:
        sell_price = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close']

    #print(f'Upper Bollinger Band: {dataframe_stockdata.at[dataframe_stockdata.index[-1], "UpperBand"]:.2f}')
    #print(f'Lower Bollinger Band: {dataframe_stockdata.at[dataframe_stockdata.index[-1], "LowerBand"]:.2f}')
    #print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')

    return buy_price, sell_price


def strategy4(dataframe_stockdata,risk_factor,money,stock_count):
    # Define the short-term and long-term periods for the EMA calculation
    short_term_period = 12
    long_term_period = 26

    # Calculate the short-term and long-term exponential moving averages (EMA)
    short_term_ema = dataframe_stockdata['Close'].ewm(span=short_term_period, adjust=False).mean()
    long_term_ema = dataframe_stockdata['Close'].ewm(span=long_term_period, adjust=False).mean()

    # Calculate the MACD line by subtracting the long-term EMA from the short-term EMA
    macd_line = short_term_ema - long_term_ema

    # Define the signal line period
    signal_line_period = 9

    # Calculate the signal line as a 9-period EMA of the MACD line
    signal_line = macd_line.ewm(span=signal_line_period, adjust=False).mean()

    # Determine the buy and sell signals based on MACD
    buy_price = 0
    sell_price = 9999999999

    if macd_line.iloc[-1]*risk_factor > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]*risk_factor and money >= dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close']:
        buy_price = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close']
    elif macd_line.iloc[-1]*risk_factor < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2]*risk_factor and stock_count>0:
        sell_price = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close']

   # print(f'MACD Line: {macd_line.iloc[-1]:.2f}')
    #print(f'Signal Line: {signal_line.iloc[-1]:.2f}')
    #print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')

    return buy_price, sell_price
