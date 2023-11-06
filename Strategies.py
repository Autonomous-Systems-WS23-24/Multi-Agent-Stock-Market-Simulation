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
