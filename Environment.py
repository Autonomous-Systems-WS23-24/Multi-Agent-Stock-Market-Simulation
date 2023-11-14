import asyncio
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import spade
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import json
import warnings
import random as rd
import talib as tl

list_stocks = ["zoes.us.txt"]

class Environment():
    def __init__(self, list_stocks):
        self.list_stocks = list_stocks
        for stock in self.list_stocks:
            self.stock_data_history = pd.read_csv('archive/Stocks/{}'.format(stock))
            self.stock_data = self.stock_data_history[10:60]

    def calc_new_stockdata(self):
        if not self.transaction_df.empty:
            print("Transactions!")
            close = rd.choice(self.transaction_df["price"].tolist())
            open = rd.choice(self.transaction_df["price"].tolist())
            low = self.transaction_df["price"].min() * rd.randrange(90, 100) / 100
            high = (self.transaction_df["price"].max() * rd.randrange(100, 110)) / 100
            new_data = pd.DataFrame({"Close": close, "Open": open, "High": high, "Low": low}, index=[0])
            self.stock_data = pd.concat([self.stock_data, new_data], ignore_index=True)

        else:
            print("No transactions! Creating artificial Data!")
            mean = (self.stock_data.at[self.stock_data.index[-1], "Low"] + self.stock_data.at[
                self.stock_data.index[-1], "High"]) / 2
            var = self.stock_data['Close'].rolling(10).std().mean()
            random_price_data = np.random.normal(mean, var, 20)
            close = random_price_data[-1]
            open = random_price_data[0]
            low = random_price_data.min()
            high = random_price_data.max()
            new_data = pd.DataFrame({"Close": close, "Open": open, "High": high, "Low": low}, index=[0])
            self.stock_data = pd.concat([self.stock_data, new_data], ignore_index=True)

    def Plot(self):
        x = np.arange(0, len(self.stock_data["Close"].to_list()))
        y = self.stock_data["Close"].to_list()
        plt.xlabel("days")
        plt.ylabel("value")
        plt.plot(x, y, label=f"Stock value")
        plt.ylim(0, max(y) * 1.1)
        plt.legend()
        plt.show()

    def stock_cue_calc(self):
        # Calculate 52-day moving average
        self.stock_data['52-day MA'] = tl.MA(self.stock_data['Close'], timeperiod=52, matype=0)
        # Calculate 26-day moving average
        self.stock_data['26-day MA'] = tl.MA(self.stock_data['Close'], timeperiod=26, matype=0)
        # Calculate Relative Strength Index (RSI)
        self.stock_data['RSI'] = tl.RSI(self.stock_data['Close'], timeperiod=14)
        # Calculate Market Index and its slope
        self.stock_data['Market Index'] = (self.stock_data['High'] + self.stock_data['Low']) / 2
        self.stock_data['Market Index Slope'] = np.gradient(self.stock_data['Market Index'])
        # Calculate Market Level - Index Average
        market_index_average = self.stock_data['Market Index'].mean()
        self.stock_data['Market Level - Index Average'] = market_index_average
        # Calculate Market Index Acceleration
        self.stock_data['Market Index Acceleration'] = np.gradient(self.stock_data['Market Index Slope'])
        # Calculate MACD
        self.stock_data['MACD'], self.stock_data['Signal'], _ = tl.MACD(self.stock_data['Close'], fastperiod=12, slowperiod=26,
                                                              signalperiod=9)
        # Calcuate Stochastic Oscillator
        self.stock_data['K'], self.stock_data['D'] = tl.STOCH(self.stock_data['High'], self.stock_data['Low'], self.stock_data['Close'],
                                                    fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3,
                                                    slowd_matype=0)
        return self.stock_data


class Orderbook():
    def __init__(self):
        pass

    # def send_transactions(self):
    #     if not self.transaction_df.empty:
    #         for investor in self.investor_list:
    #             msg = Message(to="{}@localhost".format(investor))  # Instantiate the message
    #             msg.set_metadata("performative", "inform")  # Set the "query" FIPA performative
    #             msg.body = self.transaction_df.to_json(orient="split")  # Set the message content
    #             await self.send(msg)
    #     else:
    #         for investor in self.investor_list:
    #             msg = Message(to="{}@localhost".format(investor))  # Instantiate the message
    #             msg.set_metadata("performative", "inform")  # Set the "query" FIPA performative
    #             msg.body = "--no transactions--"
    #             await self.send(msg)

    # def do_transactions(self):
    #     offerbook = self.offerbook
    #     df_buy_sorted = offerbook.sort_values(by="buy", ascending=False).reset_index(drop=True)
    #     df_sell_sorted = offerbook.sort_values(by="sell").reset_index(drop=True)
    #     transactions = []  # Initialize an empty list for transactions
    #     matched_buyers = set()
    #     matched_sellers = set()
    #
    #     for index in range(len(df_buy_sorted.index)):
    #         buyer_name = df_buy_sorted["name"][index]
    #         seller_name = df_sell_sorted["name"][index]
    #
    #         if buyer_name == seller_name:
    #             continue  # Skip matching the buyer and seller with the same name
    #
    #         if buyer_name not in matched_buyers and seller_name not in matched_sellers and df_buy_sorted["buy"][
    #             index] >= df_sell_sorted["sell"][index]:
    #             transaction_value = round((df_sell_sorted["sell"][index] + df_buy_sorted["buy"][index]) / 2, 2)
    #             transaction = {"buyer": buyer_name, "seller": seller_name, "price": transaction_value}
    #             transactions.append(transaction)
    #
    #             matched_buyers.add(buyer_name)
    #             matched_sellers.add(seller_name)
    #         # Convert the list of dictionaries into a DataFrame
    #         else:
    #             break
    #     self.transaction_df = pd.DataFrame(transactions)




list_stocks = ["zoes.us.txt"]
environment = Environment(list_stocks)

stocksdata = environment.stock_cue_calc()
print(stocksdata)