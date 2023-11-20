import talib as tl
import numpy as np
import pandas as pd



#Stategy 1 is a short-term strategy using RSI for calculating buy and sell prizes
def strategy1(jid, stockdata_dict, list_stocks, risk_factor, money, security_register, opinions, social_influence, time_factor, influencibility_index):
    offer = {}
    new_opinion = {}
    for stock, index in zip(list_stocks, range(len(list_stocks))):
        # initialize values
        stock_count = security_register.at[jid, stock]
        stockdata = stockdata_dict[stock]
        opinion_self_stock = opinions.at[0,stock]
        opinion_social_stock = social_influence.at[0,stock]
        money_to_spend = ((1-influencibility_index)*opinion_self_stock + influencibility_index*opinion_social_stock) * money
        n = 1
        sell_price = np.nan
        buy_price = np.nan

        # calculate current prices
        price_low = stockdata.at[stockdata.index[-1], "Low"]
        price_high = stockdata.at[stockdata.index[-1], "High"]
        price_mean = (price_low + price_high) / 2

        # calculate RSI
        time_period = int(time_factor * 100) #days
        stockdata["RSI"] = tl.RSI(stockdata['Close'], timeperiod=time_period)
        rsi_mean = stockdata["RSI"].mean()
        rsi_std = stockdata["RSI"].std()
        RSI_buy_threshold = rsi_mean - 0.01 * rsi_std
        RSI_sell_threshold = rsi_mean + 0.01 * rsi_std

        #moving average
        stockdata["MA"] = tl.MA(stockdata['Close'], timeperiod=time_period, matype=0)
        # conditions for creating buy and sell offers
        if (stockdata.at[stockdata.index[-1], "RSI"] < RSI_buy_threshold
                and price_mean <= stockdata.at[stockdata.index[-1], "MA"]) and money_to_spend >= price_mean:

            buy_price = price_mean
            n = int(np.floor(money_to_spend/buy_price))
            if n == 0:
                sell_price = np.nan
                buy_price = np.nan



        elif (stockdata.at[stockdata.index[-1], "RSI"] > RSI_sell_threshold
              and price_low >= stockdata.at[stockdata.index[-1], "MA"]) and stock_count > 0:
            sell_price = price_mean
            n = stock_count

        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n}, index=[0])


        new_opinion[stock] = round(abs(0.5-stockdata.at[stockdata.index[-1], "RSI"]),2)

    new_opinions = pd.DataFrame(new_opinion, index=[0])
    new_opinions = new_opinions.div(new_opinions.sum(axis=1), axis=0)


    return offer, new_opinions


#Strategy 2 uses Bollinger bands for calculating buy and sell prices
def strategy2(jid, stockdata_dict, list_stocks, risk_factor, money, security_register, opinions, social_influence, time_factor,  influencibility_index):
    offer = {}
    total_buy_price = 0
    new_opinion = {}
    for stock, index in zip(list_stocks, range(len(list_stocks))):
        # Initialize values
        stock_count = security_register.at[jid, stock]
        stockdata = stockdata_dict[stock]
        opinion_self_stock = opinions.at[0, stock]
        opinion_social_stock = social_influence.at[0, stock]
        money_to_spend = ((1 - influencibility_index) * opinion_self_stock + influencibility_index * opinion_social_stock) * money
        n = 1
        sell_price = np.nan
        buy_price = np.nan

        # Calculate current prices
        price_low = stockdata.at[stockdata.index[-1], "Low"]
        price_high = stockdata.at[stockdata.index[-1], "High"]
        price_mean = (price_low + price_high) / 2

        # Calculate Bollinger Bands
        bb_period = int(100 * time_factor) # days
        num_std_dev = 2
        stockdata['RollingMean'] = stockdata['Close'].rolling(bb_period).mean()
        stockdata['RollingStd'] = stockdata['Close'].rolling(bb_period).std()
        stockdata['UpperBand'] = stockdata['RollingMean'] + (num_std_dev * stockdata['RollingStd'])
        stockdata['LowerBand'] = stockdata['RollingMean'] - (num_std_dev * stockdata['RollingStd'])

        # Conditions for creating buy and sell offers using Bollinger Bands
        if price_mean < stockdata.at[stockdata.index[-1], 'LowerBand'] and money_to_spend >= price_mean:
            buy_price = stockdata.at[stockdata.index[-1],'RollingMean']
            n = int(np.floor(money_to_spend / buy_price))
            if n == 0:
                sell_price = np.nan
                buy_price = np.nan

        elif price_mean > stockdata.at[stockdata.index[-1], 'UpperBand'] and stock_count >= n:
            sell_price = stockdata.at[stockdata.index[-1],'RollingMean']
            n = stock_count

        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n}, index=[0])
        new_opinion[stock] = abs((stockdata.at[stockdata.index[-1],"RollingMean"]-stockdata.at[stockdata.index[-1],"Close"])/stockdata.at[stockdata.index[-1],"RollingMean"])


    new_opinions = pd.DataFrame(new_opinion, index=[0])
    new_opinions = new_opinions.div(new_opinions.sum(axis=1), axis=0)



    return offer, new_opinions


#Strategy 3 uses the stochastic oscillator and moving average of the last 52 days
def strategy3(jid, stockdata_dict, list_stocks, risk_factor, money, security_register, opinions, social_influence,time_factor, influencibility_index):
    total_buy_price = 0
    offer = {}
    new_opinion = {}
    significance_scores = {}
    for stock, index in zip(list_stocks, range(len(list_stocks))):
        # initialize values
        stock_count = security_register.at[jid, stock]
        stockdata = stockdata_dict[stock]
        opinion_self_stock = opinions.at[0, stock]
        opinion_social_stock = social_influence.at[0, stock]
        money_to_spend = ((1 - influencibility_index) * opinion_self_stock + influencibility_index * opinion_social_stock) * money
        n = 1
        buy_price = np.nan
        sell_price = np.nan

        #Calculate current prices
        price_low = stockdata.at[stockdata.index[-1], "Low"]
        price_high = stockdata.at[stockdata.index[-1], "High"]
        price_mean = (price_low + price_high) / 2

        k_period, d_period = int(50 * time_factor), int(10 * time_factor) #days
        stockdata['%K'] = 100 * ((stockdata['Close'] - stockdata['Low'].rolling(window=k_period).min()) /
                                 (stockdata['High'].rolling(window=k_period).max() - stockdata['Low'].rolling(window=k_period).min()))
        stockdata['%D'] = stockdata['%K'].rolling(window=d_period).mean()

        # moving average
        time_period = int(50 * time_factor)
        stockdata["MA"] = tl.MA(stockdata['Close'], timeperiod=time_period, matype=0)


        if price_mean < stockdata.at[stockdata.index[-1], "MA"] and money_to_spend >= price_mean and stockdata['%K'].iloc[-1] < 20:
            buy_price = stockdata.at[stockdata.index[-1], "MA"]
            n = int(np.floor(money_to_spend / buy_price))
            if n == 0:
                sell_price = np.nan
                buy_price = np.nan


        elif price_mean > stockdata.at[stockdata.index[-1], "MA"] and stock_count > 0 and stockdata['%K'].iloc[-1] > 80:
            sell_price = stockdata['Close'].rolling(window=k_period).mean()
            n = stock_count

        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n}, index=[0])
        new_opinion[stock] = abs(stockdata.at[stockdata.index[-1],"%D"])


    new_opinions = pd.DataFrame(new_opinion, index=[0])
    new_opinions = new_opinions.div(new_opinions.sum(axis=1), axis=0)



    return offer, new_opinions


#Strategy 4 uses Exponential Moving Average (EMA) to calculate buy and sell prizes
def strategy4(jid, stockdata_dict, list_stocks, risk_factor, money, security_register, opinions, social_influence,time_factor,influencibility_index):
    total_buy_price = 0
    offer = {}
    new_opinion = {}
    significance_scores = {}
    for stock, index in zip(list_stocks, range(len(list_stocks))):
        #Initialize values
        stock_count = security_register.at[jid, stock]
        stockdata = stockdata_dict[stock]
        opinion_self_stock = opinions.at[0, stock]
        opinion_social_stock = social_influence.at[0, stock]
        money_to_spend = ((1 - influencibility_index) * opinion_self_stock + influencibility_index * opinion_social_stock) * money
        n = 1
        buy_price = np.nan
        sell_price = np.nan

        #Calculate currents prizes
        price_low = stockdata.at[stockdata.index[-1], "Low"]
        price_high = stockdata.at[stockdata.index[-1], "High"]
        price_mean = (price_low + price_high) / 2

        #Calculating Exponential Moving Average (EMA)
        short_term_period, long_term_period = int(26 * time_factor), int(50 * time_factor) #days
        short_term_ema = stockdata['Close'].ewm(span=short_term_period, adjust=False).mean()
        long_term_ema = stockdata['Close'].ewm(span=long_term_period, adjust=False).mean()
        macd_line = short_term_ema - long_term_ema
        signal_line_period = 9 #stays constant
        signal_line = macd_line.ewm(span=signal_line_period, adjust=False).mean()
        position_size = max(1, int((money) / price_mean))


        if macd_line.iloc[-1] > signal_line.iloc[-1] and money >= stockdata.at[stockdata.index[-1], 'Close']:
            buy_price =  short_term_ema.iloc[-1]
            n = int(np.floor(money_to_spend / buy_price))
            if n == 0:
                sell_price = np.nan
                buy_price = np.nan

        elif macd_line.iloc[-1] < signal_line.iloc[-1] and stock_count > 0:
            sell_price = short_term_ema.iloc[-1]
            n = stock_count

        offer[stock] = pd.DataFrame({"buy": buy_price, "sell": sell_price, "quantity": n}, index=[0])
        new_opinion[stock] = abs(short_term_ema.iloc[-1]-stockdata.at[stockdata.index[-1],"Close"]/short_term_ema.iloc[-1])


    new_opinions = pd.DataFrame(new_opinion, index=[0])
    new_opinions = new_opinions.div(new_opinions.sum(axis=1), axis=0)


    return offer, new_opinions
