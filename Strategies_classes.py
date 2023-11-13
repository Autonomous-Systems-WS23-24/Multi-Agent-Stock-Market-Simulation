import pandas as pd
import numpy as np

class Strategy1():
    def __str__(self):
        return 'Strategy 1'
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
    def __str__(self):
        return 'Strategy 2'
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


class Strategy3():
    def __str__(self):
        return 'Strategy 3'
    def __init__(self, dataframe_stockdata):
        self.sma_period = 25
        self.price_low = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Low']
        self.price_high = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'High']
        self.price_mean = (self.price_low + self.price_high) / 2
        # moving average of last 52 days
        self.MA52 = dataframe_stockdata.at[dataframe_stockdata.index[-1], '52-day MA']
        self.sma = dataframe_stockdata["Close"][-self.sma_period:].mean()
    def execute(self, jid):
        # Calculate a simple moving average (SMA) over the last N periods.
       # print(f'SMA of last {self.sma_period} days: {self.sma} ')

        # Buying if the mean is higher than the sma
        if self.price_mean > self.sma:
            self.buy_price = self.price_mean
        else:
            self.buy_price = 0
        # Selling if the mean is lower than the sma
        if self.price_mean < self.sma:
            self.sell_price = self.price_mean
        else:
            self.sell_price = 9999999999
        
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
    
class strategy4():
    def strategy_SMA(self,dataframe_stockdata):
        self.price_low = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Low']
        self.price_high = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'High']
        self.price_mean = (self.price_low + self.price_high) / 2

        # Calculate a simple moving average (SMA) over the last 25 days. 
        self.sma_period = 25
        self.sma = dataframe_stockdata[-self.sma_period:].mean()
        #print(f'SMA of last {self.sma_period} days: {self.sma} ')
        
    def execute(self,jid):
        #Buying if the mean is higher than the sma
        if self.price_mean > self.sma :
            buy_price = self.price_mean 
        else:
            buy_price = 0
        #Selling if the mean is lower than the sma
        if self.price_mean < self.sma:
            sell_price = self.price_mean
        else:
            sell_price = 9999999999

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

class strategy5():
    def strategy_BollingerBands(self,dataframe_stockdata):
        # Define the period for Bollinger Bands calculation and the number of standard deviations
        self.bb_period = 20
        self.num_std_dev = 2
        # Calculate the rolling mean and standard deviation of the closing prices, 
        dataframe_stockdata['RollingMean'] = dataframe_stockdata['Close'].rolling(self.bb_period).mean()
        dataframe_stockdata['RollingStd'] = dataframe_stockdata['Close'].rolling(self.bb_period).std()
        # Calculate the upper and lower Bollinger Bands
        dataframe_stockdata['UpperBand'] = dataframe_stockdata['RollingMean'] + (self.num_std_dev * dataframe_stockdata['RollingStd'])
        dataframe_stockdata['LowerBand'] = dataframe_stockdata['RollingMean'] - (self.num_std_dev * dataframe_stockdata['RollingStd'])

        self.Lowerband=dataframe_stockdata.at[dataframe_stockdata.index[-1], 'LowerBand']
        self.UpperBand=dataframe_stockdata.at[dataframe_stockdata.index[-1], 'UpperBand']
        self.price_close = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close']
        print(f'Upper Bollinger Band: {dataframe_stockdata.at[dataframe_stockdata.index[-1], "UpperBand"]:.2f}')
        print(f'Lower Bollinger Band: {dataframe_stockdata.at[dataframe_stockdata.index[-1], "LowerBand"]:.2f}')
        

    def execute(self,jid):
        # Determine the buy and sell signals based on Bollinger Bands
        self.buy_price = 0
        self.sell_price = 9999999999
        
        if self.price_close < self.Lowerband:
            self.buy_price = self.price_close
        else:
            self.buy_price = 0

        if self.price_close > self.UpperBand:
            self.sell_price = self.price_close
        else:
            self.sell_price = 9999999999

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

class strategy6():
    def strategy_MACD(self,dataframe_stockdata):
        # Define the short-term and long-term periods for the EMA calculation
        self.short_term_period = 12
        self.long_term_period = 26

        # Calculate the short-term and long-term exponential moving averages (EMA)
        self.short_term_ema = dataframe_stockdata['Close'].ewm(span=self.short_term_period, adjust=False).mean()
        self.long_term_ema = dataframe_stockdata['Close'].ewm(span=self.long_term_period, adjust=False).mean()

        # Calculate the MACD line by subtracting the long-term EMA from the short-term EMA
        self.macd_line = self.short_term_ema - self.long_term_ema

        # Define the signal line period
        self.signal_line_period = 9

        # Calculate the signal line as a 9-period EMA of the MACD line
        self.signal_line = self.macd_line.ewm(span=self.signal_line_period, adjust=False).mean()
        
    def execute(self,jid):
        # Determine the buy and sell signals based on MACD
        if self.macd_line.iloc[-1] > self.signal_line.iloc[-1] and self.macd_line.iloc[-2] <= self.signal_line.iloc[-2]:
            self.buy_price = self.price_close
        else:
            self.buy_price = 0

        if self.macd_line.iloc[-1] < self.signal_line.iloc[-1] and self.macd_line.iloc[-2] >= self.signal_line.iloc[-2]:
            self.sell_price = self.price_close
        else:
            self.sell_price = 9999999999

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