def strategy_one(dataframe_stockdata):
    # The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements.
    # It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
    RSI_value = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'RSI']
    price_low = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Low']
    price_high = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'High']
    price_mean = (price_low + price_high) / 2
    # moving average of last 52 days
    MA52 = dataframe_stockdata.at[dataframe_stockdata.index[-1], '52-day MA']
    print(f'RSI: {RSI_value}', f'MA of alst 52 days: {MA52}')
    # buying when RSI value is lower than 35, and the mean price is 5 euro lower than the MA52. Buy the stock for the mean price
    if RSI_value < 35 and price_mean <= (MA52 - 5):
        buy_price = price_mean - 5
    else:
        buy_price = 0
    # selling when RSI value is higher than 40 or if the low price is 5 lower than MA52. Sell the stock for the mean price
    if RSI_value > 40 or price_low <= (MA52 - 5):
        sell_price = price_mean
    else:
        sell_price = 9999999999
    print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')
    return buy_price, sell_price



def strategy_SMA(dataframe_stockdata):
    price_low = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Low']
    price_high = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'High']
    price_mean = (price_low + price_high) / 2

    # Calculate a simple moving average (SMA) over the last N periods. 
    sma_period = 25
    sma = dataframe_stockdata[-sma_period:].mean()
    print(f'SMA of last {sma_period} days: {sma} ')

    #Buying if the mean is higher than the sma
    if price_mean > sma :
        buy_price = price_mean 
    else:
        buy_price = 0
    #Selling if the mean is lower than the sma
    if price_mean < sma:
        sell_price = price_mean
    else:
        sell_price = 9999999999
    print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')
    return buy_price, sell_price




def strategy_BollingerBands(dataframe_stockdata):
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

    if dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close'] < dataframe_stockdata.at[dataframe_stockdata.index[-1], 'LowerBand']:
        buy_price = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close']
    elif dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close'] > dataframe_stockdata.at[dataframe_stockdata.index[-1], 'UpperBand']:
        sell_price = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close']

    print(f'Upper Bollinger Band: {dataframe_stockdata.at[dataframe_stockdata.index[-1], "UpperBand"]:.2f}')
    print(f'Lower Bollinger Band: {dataframe_stockdata.at[dataframe_stockdata.index[-1], "LowerBand"]:.2f}')
    print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')

    return buy_price, sell_price