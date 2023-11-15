import talib as tl
import numpy as np
import pandas as pd

def strategy1(jid, stockdata_dict, list_stocks, risk_factor, money, security_register, opinions, social_influence):
    offer = {}
    significance_scores = {}
    for stock in list_stocks:
        stock_count = security_register[stock][jid[0]]
        stockdata = stockdata_dict[stock]
        n=1
        # The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements.
        # It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
        stockdata["RSI"] = tl.RSI(stockdata['Close'], timeperiod=14)
        price_low = stockdata.at[stockdata.index[-1], 'Low']
        price_high = stockdata.at[stockdata.index[-1], 'High']
        price_mean = (price_low + price_high) / 2
        # moving average of last 52 days
        stockdata["MA"] = tl.MA(stockdata['Close'], timeperiod=26, matype=0)
        sell_price = np.nan
        buy_price = np.nan
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
        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n },index=[0])
        significance_scores[stock] = stockdata["RSI"].mean
   # new_offer = modifyoffer(opininos,social_influence)    we here put a linear transform on the offers dependent on personal beliefs and social influences

    return offer

def strategy2(stockdata, stock_list, risk_factor, money, security_register, opinions, social_influence):
    offer = {}
    significance_scores = {}

    for stock in stock_list:
        stock_count = security_register[stock][jid[0]]
        stockdata = stockdata_dict[stock]
        n=1

        # Added Stochastic Oscillator in buy and sell conditions
        price_low = stockdata.at[stockdata.index[-1], 'Low']
        price_high = stockdata.at[stockdata.index[-1], 'High']
        price_mean = (price_low + price_high) / 2

        k_period = 14
        d_period = 3
        stockdata['%K'] = 100 * ((stockdata['Close'] - stockdata['Low'].rolling(window=k_period).min()) / (stockdata['High'].rolling(window=k_period).max() - stockdata['Low'].rolling(window=k_period).min()))
        stockdata['%D'] = stockdata['%K'].rolling(window=d_period).mean()

        # moving average of last 25 days
        sma_period = 25
        stockdata["SMA"] = tl.MA(stockdata['Close'], timeperiod=sma_period, matype=0)
        buy_price = np.nan
        sell_price = np.nan

        # Calculate position size based on risk factor and available capital
        position_size = max(1, int((risk_factor * money) / price_mean))

        confidence = -risk_factor if risk_factor < 0.03 else risk_factor

        # Calculate a simple moving average (SMA) over the last N periods.
        # Buying if the mean is higher than the sma
        if (
            price_mean < stockdata.at[stockdata.index[-1], "SMA"] and money >= price_mean
            and stockdata['%K'].iloc[-1] < 20
        ):
            buy_price = price_mean + confidence * 5
            if money > 5 * buy_price:
                n = min(position_size, 5)

        # Selling if the mean is lower than the sma
        elif (
            price_mean > stockdata.at[stockdata.index[-1], "SMA"] and stock_count > 0
            and stockdata['%K'].iloc[-1] > 80
        ):
            sell_price = price_mean - confidence * 5
            if stock_count >= 5:
                n = min(position_size, stock_count)

        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n}, index=[0])
        significance_scores[stock] = stockdata["%K"].mean

    return offer

def strategy3(stockdata, stock_list, risk_factor, money, security_register, opinions, social_influence):
    offer = {}
    significance_scores = {}

    for stock in stock_list:
        stock_count = security_register[stock][jid[0]]
        stockdata = stockdata_dict[stock]
        n = 1

        # Define the period for Bollinger Bands calculation and the number of standard deviations
        bb_period = 20
        num_std_dev = 2
        price_low = stockdata.at[stockdata.index[-1], 'Low']
        price_high = stockdata.at[stockdata.index[-1], 'High']
        price_mean = (price_low + price_high) / 2
        # Calculate the rolling mean and standard deviation of the closing prices,
        stockdata['RollingMean'] = stockdata['Close'].rolling(bb_period).mean()
        stockdata['RollingStd'] = stockdata['Close'].rolling(bb_period).std()

        # Calculate the upper and lower Bollinger Bands
        stockdata['UpperBand'] = stockdata['RollingMean'] + (num_std_dev * stockdata['RollingStd'])
        stockdata['LowerBand'] = stockdata['RollingMean'] - (num_std_dev * stockdata['RollingStd'])

        buy_price = np.nan
        sell_price = np.nan

        # Calculate position size based on risk factor and available capital
        position_size = max(1, int((risk_factor * money) / price_mean))
        confidence = -risk_factor if risk_factor < 0.03 else risk_factor

        if (
            stockdata.at[stockdata.index[-1], 'Close'] < stockdata.at[stockdata.index[-1], 'LowerBand']
            and money >= stockdata.at[stockdata.index[-1], 'Close']
        ):
            buy_price = price_mean + confidence * 5
            if money > 5 * buy_price:
                n = min(position_size, 5)
        elif (
            stockdata.at[stockdata.index[-1], 'Close'] > stockdata.at[stockdata.index[-1], 'UpperBand']
            and stock_count > 0
        ):
            sell_price = price_mean - confidence * 5
            if stock_count >= 5:
                n = min(position_size, stock_count)

        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n}, index=[0])
        significance_scores[stock] = stockdata['Close'].mean

    return offer

def strategy4(stockdata, stock_list, risk_factor, money, security_register, opinions, social_influence):
    offer = {}
    significance_scores = {}

    for stock in stock_list:
        stock_count = security_register[stock][jid[0]]
        stockdata = stockdata_dict[stock]
        n = 1

        # Define the short-term and long-term periods for the EMA calculation
        short_term_period = 12
        long_term_period = 26
        price_low = stockdata.at[stockdata.index[-1], 'Low']
        price_high = stockdata.at[stockdata.index[-1], 'High']
        price_mean = (price_low + price_high) / 2
        # Calculate the short-term and long-term exponential moving averages (EMA)
        short_term_ema = stockdata['Close'].ewm(span=short_term_period, adjust=False).mean()
        long_term_ema = stockdata['Close'].ewm(span=long_term_period, adjust=False).mean()

        # Calculate the MACD line by subtracting the long-term EMA from the short-term EMA
        macd_line = short_term_ema - long_term_ema

        # Define the signal line period
        signal_line_period = 9

        # Calculate the signal line as a 9-period EMA of the MACD line
        signal_line = macd_line.ewm(span=signal_line_period, adjust=False).mean()

        buy_price = np.nan
        sell_price = np.nan

        # Calculate position size based on risk factor and available capital
        position_size = max(1, int((risk_factor * money) / price_mean))
        confidence = -risk_factor if risk_factor < 0.03 else risk_factor

        if (
            macd_line.iloc[-1] > signal_line.iloc[-1]
            and money >= stockdata.at[stockdata.index[-1], 'Close']
        ):
            buy_price = price_mean + confidence * 5
            if money > 5 * buy_price:
                n = min(position_size, 5)

        elif (
            macd_line.iloc[-1] < signal_line.iloc[-1] and stock_count > 0
        ):
            sell_price = price_mean + confidence * 5
            if stock_count >= 5:
                n = min(position_size, stock_count)

        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n}, index=[0])
        significance_scores[stock] = macd_line.mean

    return offer


