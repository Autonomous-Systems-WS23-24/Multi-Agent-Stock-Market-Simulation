import talib as tl
import numpy as np
import pandas as pd

def strategy1(jid, stockdata_dict, list_stocks, risk_factor, money, security_register, opinions, social_influence):
    offer = {}
    for stock in list_stocks:
        stock_count = security_register[stock]
        stock_count = stock_count.loc[f'{jid}','quantity']
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
   # new_offer = modifyoffer(opininos,social_influence)    we here put a linear transform on the offers dependent on personal beliefs and social influences

    return offer


