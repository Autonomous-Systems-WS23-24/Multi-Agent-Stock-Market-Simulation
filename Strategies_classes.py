import pandas as pd
import numpy as np

class Strategy1():
    def __init__(self, dataframe_stockdata):
        # The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements.
        # It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
        self.RSI_value = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'RSI']
        self.price_low = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Low']
        self.price_high = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'High']
        self.price_mean = (self.price_low + self.price_high) / 2
        # moving average of last 52 days
        self.MA52 = dataframe_stockdata.at[dataframe_stockdata.index[-1], '52-day MA']

    def execute(self, jid):
        #print(f'RSI: {self.RSI_value}', f'MA of alst 52 days: {self.MA52}')
        # buying when RSI value is lower than 35, and the mean price is 5 euro lower than the MA52. Buy the stock for the mean price
        if self.RSI_value < 35 and self.price_mean <= (self.MA52 - 5):
            self.buy_price = self.price_mean - 5
        else:
            self.buy_price = 0
        # selling when RSI value is higher than 40 or if the low price is 5 lower than MA52. Sell the stock for the mean price
        if self.RSI_value > 40 or self.price_low <= (self.MA52 - 5):
            self.sell_price = self.price_mean
        else:
            self.sell_price = 9999999

        if self.buy_price >= self.sell_price:
            self.sell_price = 9999999

        self.jid = jid
        self.orderbook_entry = {
            "name": [self.jid[0]],
            "sell": [self.sell_price],
            "buy": [self.buy_price]
        }

        #print(f'{self.jid} wants to sell for {self.sell_price} and buy for {self.buy_price}')
        return self.orderbook_entry



class Strategy2():
    def __init__(self, dataframe_stockdata):
        # The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements.
        # It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
        self.RSI_value = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'RSI']
        self.price_low = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Low']
        self.price_high = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'High']
        self.price_mean = (self.price_low + self.price_high) / 2
        # moving average of last 52 days
        self.MA52 = dataframe_stockdata.at[dataframe_stockdata.index[-1], '52-day MA']

    def execute(self, jid):
        #print(f'RSI: {self.RSI_value}', f'MA of alst 52 days: {self.MA52}')
        # buying when RSI value is lower than 50, and the mean price is 2 euro lower than the MA52. Buy the stock for the mean price -2
        if self.RSI_value < 5 and self.price_mean <= (self.MA52 - 2):
            self.buy_price = self.price_mean - 2
        else:
            self.buy_price = 0
        # selling when RSI value is higher than 60 or if the low price is 20 lower than MA52. Sell the stock for the mean price -20
        if self.RSI_value > 10 or self.price_low <= (self.MA52 - 20):
            self.sell_price = self.price_mean - 20
        else:
            self.sell_price = 9999999

        if self.buy_price >= self.sell_price:
            self.sell_price = 9999999

        self.jid = jid
        self.orderbook_entry = {
            "name": [self.jid[0]],
            "sell": [self.sell_price],
            "buy": [self.buy_price]
        }

        #print(f'{self.jid} wants to sell for {self.sell_price} and buy for {self.buy_price}')
        return self.orderbook_entry

