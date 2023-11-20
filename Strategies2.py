import talib as tl
import numpy as np
import pandas as pd


def strategy1(jid, stockdata_dict, list_stocks, risk_factor, money, security_register, opinions, social_influence):
    total_buy_price = 0
    offer = {}
    significance_scores = {}
    for stock in list_stocks:
    #initialize values
        stock_count = security_register.at[jid, stock]
        stockdata = stockdata_dict[stock]
        n=1
        sell_price = np.nan
        buy_price = np.nan

    #calculate current prices
        price_low = stockdata.at[stockdata.index[-1], "Low"]
        price_high = stockdata.at[stockdata.index[-1], "High"]
        price_mean = (price_low + price_high) / 2

    #calulate interesting cues:
        #RSI, The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements. It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
        stockdata["RSI"] = tl.RSI(stockdata['Close'], timeperiod=14) # The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements.  # It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
        rsi_mean = stockdata["RSI"].mean()
        rsi_std = stockdata["RSI"].std()
        RSI_buy_threshold = rsi_mean - 0.01 * rsi_std
        RSI_sell_threshold = rsi_mean + 0.01 * rsi_std

        #moving average of last 52 days
        stockdata["MA"] = tl.MA(stockdata['Close'], timeperiod=52, matype=0)


        #A part where we look at popularity and future prospect of a stock
        opinions = []
        social_influence = []


    #conditions for creating buy and sell offers
        if (stockdata.at[stockdata.index[-1],"RSI"] < RSI_buy_threshold
                or price_mean <= stockdata.at[stockdata.index[-1],"MA"]) and money> price_mean:

            if money > n*price_high:
                buy_price = price_mean * 0.97
                total_buy_price += (n * buy_price)
                money-= buy_price*n
        elif (stockdata.at[stockdata.index[-1],"RSI"] > RSI_sell_threshold
                or price_low >= stockdata.at[stockdata.index[-1],"MA"]) and stock_count>0:
            sell_price = (price_mean +price_high)/2
            #print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')
        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n },index=[0])


    #Also we need a way of choosing of which order we want to execute
    #new_offer = modifyoffer(opininos,social_influence)    we here put a linear transform on the offers dependent on personal beliefs and social influences
    #expected_return = (future_price_estimate - buy_price) / buy_price
    #preference = expected_return - risk_factor
   # for stock in list_stocks:
    #    n = offer[stock]["quantity"].iloc[0]
     #   # Check if total_buy_price is not zero to avoid division by zero
      #  if total_buy_price != 0:
       #     offer[stock]["quantity"].iloc[0] = np.floor(n * money / total_buy_price)

    return offer

def strategy2(jid, stockdata_dict, list_stocks, risk_factor, money, security_register, opinions, social_influence):
    offer = {}
    total_buy_price = 0
    for stock in list_stocks:
        # Initialize values
        stock_count = security_register.at[jid, stock]
        stockdata = stockdata_dict[stock]
        n = 1
        sell_price = np.nan
        buy_price = np.nan

        # Calculate current prices
        price_low = stockdata.at[stockdata.index[-1], "Low"]
        price_high = stockdata.at[stockdata.index[-1], "High"]
        price_mean = (price_low + price_high) / 2

        # Calculate Bollinger Bands
        bb_period = 20
        num_std_dev = 2
        stockdata['RollingMean'] = stockdata['Close'].rolling(bb_period).mean()
        stockdata['RollingStd'] = stockdata['Close'].rolling(bb_period).std()
        stockdata['UpperBand'] = stockdata['RollingMean'] + (num_std_dev * stockdata['RollingStd'])
        stockdata['LowerBand'] = stockdata['RollingMean'] - (num_std_dev * stockdata['RollingStd'])

        # Conditions for creating buy and sell offers using Bollinger Bands
        if price_mean < stockdata.at[stockdata.index[-1], 'LowerBand'] and money >= price_mean:
            buy_price = price_mean
            if money > 5 * buy_price:
                n = 5  # Adjust quantity based on available funds
            total_buy_price += (n * buy_price)
            money-= n*buy_price
        elif price_mean > stockdata.at[stockdata.index[-1], 'UpperBand'] and stock_count >= n:
            sell_price = price_mean
            n = min(n, stock_count)  # Adjust quantity based on the number of stocks held

        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n}, index=[0])
   # for stock in list_stocks:
    #    n = offer[stock]["quantity"].iloc[0]
        # Check if total_buy_price is not zero to avoid division by zero
     #   if total_buy_price != 0:
      #      offer[stock]["quantity"].iloc[0] = np.floor(n * money / total_buy_price)

    return offer

def strategy3(jid, stockdata_dict, list_stocks, risk_factor, money, security_register, opinions, social_influence):
    total_buy_price = 0
    offer = {}
    significance_scores = {}
    for stock in list_stocks:
        stock_count = security_register.at[jid, stock]
        stockdata = stockdata_dict[stock]
        n = 1
        price_low = stockdata.at[stockdata.index[-1], "Low"]
        price_high = stockdata.at[stockdata.index[-1], "High"]
        price_mean = (price_low + price_high) / 2

        k_period = 14
        d_period = 3
        stockdata['%K'] = 100 * ((stockdata['Close'] - stockdata['Low'].rolling(window=k_period).min()) /
                                 (stockdata['High'].rolling(window=k_period).max() - stockdata['Low'].rolling(window=k_period).min()))
        stockdata['%D'] = stockdata['%K'].rolling(window=d_period).mean()

        # moving average of last 25 days
        sma_period = 25
        stockdata["MA"] = tl.MA(stockdata['Close'], timeperiod=sma_period, matype=0)
        buy_price = np.nan
        sell_price = np.nan

        position_size = max(1, int((risk_factor * money) / price_mean))
        confidence = -risk_factor if risk_factor < 0.03 else risk_factor

        if (
            price_mean < stockdata.at[stockdata.index[-1], "MA"] and money >= price_mean
            and stockdata['%K'].iloc[-1] < 20
        ):
            buy_price = price_mean
            if money > 5 * buy_price:
                n = min(position_size, 5)
            total_buy_price += buy_price
            money-= buy_price*n
        elif (
            price_mean > stockdata.at[stockdata.index[-1], "MA"] and stock_count > 0
            and stockdata['%K'].iloc[-1] > 80
        ):
            sell_price = price_mean
            if stock_count >= 5:
                n = min(position_size, stock_count)

        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n}, index=[0])
        significance_scores[stock] = stockdata['%K'].mean()
    #for stock in list_stocks:
     #   n = offer[stock]["quantity"].iloc[0]
        # Check if total_buy_price is not zero to avoid division by zero
      #  if total_buy_price != 0:
       #     offer[stock]["quantity"].iloc[0] = np.floor(n * money / total_buy_price)

    return offer


def strategy4(jid, stockdata_dict, list_stocks, risk_factor, money, security_register, opinions, social_influence):
    total_buy_price = 0
    offer = {}
    significance_scores = {}
    for stock in list_stocks:
        stock_count = security_register.at[jid, stock]
        stockdata = stockdata_dict[stock]
        n = 1
        short_term_period = 12
        long_term_period = 26
        price_low = stockdata.at[stockdata.index[-1], "Low"]
        price_high = stockdata.at[stockdata.index[-1], "High"]
        price_mean = (price_low + price_high) / 2

        short_term_ema = stockdata['Close'].ewm(span=short_term_period, adjust=False).mean()
        long_term_ema = stockdata['Close'].ewm(span=long_term_period, adjust=False).mean()

        macd_line = short_term_ema - long_term_ema

        signal_line_period = 9
        signal_line = macd_line.ewm(span=signal_line_period, adjust=False).mean()

        buy_price = np.nan
        sell_price = np.nan

        position_size = max(1, int((money) / price_mean))

        if macd_line.iloc[-1] > signal_line.iloc[-1] and money >= stockdata.at[stockdata.index[-1], 'Close']:
            buy_price = price_mean
            if money > 5 * buy_price:
                n = min(position_size, 5)
            total_buy_price+= buy_price
            money-= buy_price*n
        elif macd_line.iloc[-1] < signal_line.iloc[-1] and stock_count > 0:
            sell_price = (price_mean + price_high)/2
            if stock_count >= 5:
                n = stock_count

        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n}, index=[0])
        significance_scores[stock] = macd_line.mean()
    #for stock in list_stocks:
     # n = offer[stock]["quantity"].iloc[0]
        # Check if total_buy_price is not zero to avoid division by zero
      #  if total_buy_price != 0:
       #     offer[stock]["quantity"].iloc[0] = np.floor(n * money / total_buy_price)

    return offer