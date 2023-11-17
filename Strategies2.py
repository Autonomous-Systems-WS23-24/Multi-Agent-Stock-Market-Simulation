import talib as tl
import numpy as np
import pandas as pd


def strategy1(jid, stockdata_dict, list_stocks, risk_factor, money, security_register, opinions, social_influence):
    offer = {}
    significance_scores = {}
    for stock in list_stocks:
    #initialize values
        stock_count = security_register.at[jid, stock]
        stockdata = stockdata_dict[stock]
        n=1
        sell_price = np.nan
        buy_price = np.nan

    #calaculate current prices
        price_low = stockdata.at[stockdata.index[-1], "Low"]
        price_high = stockdata.at[stockdata.index[-1], "High"]
        price_mean = (price_low + price_high) / 2

    #calulate interesting cues:
        #RSI, The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements. It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
        stockdata["RSI"] = tl.RSI(stockdata['Close'], timeperiod=14) # The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements.  # It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
        rsi_mean = stockdata["RSI"].mean()
        rsi_std = stockdata["RSI"].std()
        RSI_buy_threshold = rsi_mean - 0.1 * rsi_std
        RSI_sell_threshold = rsi_mean + 0.1 * rsi_std

        #moving average of last 52 days
        stockdata["MA"] = tl.MA(stockdata['Close'], timeperiod=52, matype=0)

        #Boilinger bands
        bb_period = 20
        num_std_dev = 2
        stockdata['RollingMean'] = stockdata['Close'].rolling(bb_period).mean()
        stockdata['RollingStd'] = stockdata['Close'].rolling(bb_period).std()
        stockdata['UpperBand'] = stockdata['RollingMean'] + (num_std_dev * stockdata['RollingStd']) #When the price continually touches the upper Bollinger Band, it can indicate an overbought signal.
        stockdata['LowerBand'] = stockdata['RollingMean'] - (num_std_dev * stockdata['RollingStd']) #If the price continually touches the lower band it can indicate an oversold signal.

        #A part where we look at popularity and future prospect of a stock
        opinions = []
        social_influence = []


    #conditions for creating buy and sell offers
        if (stockdata.at[stockdata.index[-1],"RSI"] < RSI_buy_threshold
                or price_mean <= stockdata.at[stockdata.index[-1],"MA"]):

            if money > n*price_high:
                buy_price = price_mean * 0.97

        elif (stockdata.at[stockdata.index[-1],"RSI"] > RSI_sell_threshold
                or price_low >= stockdata.at[stockdata.index[-1],"MA"]):

            if stock_count >= n:
                sell_price = price_high




            #print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')
        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n },index=[0])


    #Also we need a way of choosing of which order we want to execute
    #new_offer = modifyoffer(opininos,social_influence)    we here put a linear transform on the offers dependent on personal beliefs and social influences
    #expected_return = (future_price_estimate - buy_price) / buy_price
    #preference = expected_return - risk_factor

    return offer


def strategy1(jid, stockdata_dict, list_stocks, risk_factor, money, security_register, opinions, social_influence):
    offer = {}
    significance_scores = {}
    for stock in list_stocks:
    #initialize values
        stock_count = security_register.at[jid, stock]
        stockdata = stockdata_dict[stock]
        n=1
        sell_price = np.nan
        buy_price = np.nan

    #calaculate current prices
        price_low = stockdata.at[stockdata.index[-1], "Low"]
        price_high = stockdata.at[stockdata.index[-1], "High"]
        price_mean = (price_low + price_high) / 2

    #calulate interesting cues:
        #RSI, The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements. It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
        stockdata["RSI"] = tl.RSI(stockdata['Close'], timeperiod=14) # The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements.  # It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
        rsi_mean = stockdata["RSI"].mean()
        rsi_std = stockdata["RSI"].std()
        RSI_buy_threshold = rsi_mean - 0.2 * rsi_std
        RSI_sell_threshold = rsi_mean + 0.2 * rsi_std

        #moving average of last 52 days
        stockdata["MA"] = tl.MA(stockdata['Close'], timeperiod=52, matype=0)

        #Boilinger bands
        bb_period = 20
        num_std_dev = 2
        stockdata['RollingMean'] = stockdata['Close'].rolling(bb_period).mean()
        stockdata['RollingStd'] = stockdata['Close'].rolling(bb_period).std()
        stockdata['UpperBand'] = stockdata['RollingMean'] + (num_std_dev * stockdata['RollingStd']) #When the price continually touches the upper Bollinger Band, it can indicate an overbought signal.
        stockdata['LowerBand'] = stockdata['RollingMean'] - (num_std_dev * stockdata['RollingStd']) #If the price continually touches the lower band it can indicate an oversold signal.

        #A part where we look at popularity and future prospect of a stock
        opinions = []
        social_influence = []


    #conditions for creating buy and sell offers
        if (stockdata.at[stockdata.index[-1],"RSI"] < RSI_buy_threshold
                or price_mean <= stockdata.at[stockdata.index[-1],"MA"]):

            if money > n*price_high:
                buy_price = price_mean * 0.90

        elif (stockdata.at[stockdata.index[-1],"RSI"] > RSI_sell_threshold
                or price_low >= stockdata.at[stockdata.index[-1],"MA"]):

            if stock_count >= n:
                sell_price = price_high




            #print(f'Investor wants to sell for {sell_price} and buy for {buy_price}')
        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n },index=[0])


    #Also we need a way of choosing of which order we want to execute
    #new_offer = modifyoffer(opininos,social_influence)    we here put a linear transform on the offers dependent on personal beliefs and social influences
    #expected_return = (future_price_estimate - buy_price) / buy_price
    #preference = expected_return - risk_factor

    return offer




