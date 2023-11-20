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


class Environment():
    def __init__(self, list_stocks,ownership_frame,list_investors):
        self.list_investors = list_investors
        self.list_stocks = list_stocks
        self.security_register = ownership_frame
        self.stock_candles = {}
        self.stock_opinions = {}
        self.stock_reputation = np.zeros(len(list_stocks))
        self.orderbook_sell_offers = {}
        self.orderbook_buy_offers = {}
        self.transaction_list_one_day = {}
        #this part is for keeping track of statistics#####################
        self.stock_reputation_history = []

        for stock in self.list_stocks:
            self.stock_candles[stock] = pd.read_csv('archive/Stocks/{}'.format(stock))[500:560]
            self.orderbook_sell_offers[stock] = pd.DataFrame(columns=["name", "sell"])
            self.orderbook_buy_offers[stock] = pd.DataFrame(columns=["name", "buy"])
            self.transaction_list_one_day[stock] = pd.DataFrame(columns=["buyer", "seller","price"])



    def put_buy_offer(self,stock,price,quantity,investor_name):
        for i in range(quantity):
            offer = pd.DataFrame({"name": investor_name, "buy":price}, index=[0])
            self.orderbook_buy_offers[stock] = pd.concat([self.orderbook_buy_offers[stock],offer],ignore_index=True)

    def put_sell_offer(self,stock,price,quantity,investor_name):
        for i in range(quantity):
            offer = pd.DataFrame({"name": investor_name, "sell": price}, index=[0])
            self.orderbook_sell_offers[stock] = pd.concat([self.orderbook_sell_offers[stock], offer],ignore_index=True)

    def do_transaction(self,stock,price,buyer_name,seller_name):
        transaction = pd.DataFrame({"buyer": buyer_name, "seller": seller_name, "price": price}, index=[0])

        # processing transaction to update security register
        buyer = transaction["buyer"].iloc[0]
        seller = transaction["seller"].iloc[0]


        self.security_register.at[buyer, stock]  += 1
        self.security_register.at[seller, stock] -= 1

        #Update orderbook
        self.transaction_list_one_day[stock] = pd.concat([self.transaction_list_one_day[stock], transaction], ignore_index=True)
        #print(self.transaction_list_one_day)
        indice_to_remove_sell = self.orderbook_sell_offers[stock][self.orderbook_sell_offers[stock]['name'].str.contains(seller_name)].head(1).index
        indice_to_remove_buy = self.orderbook_buy_offers[stock][self.orderbook_buy_offers[stock]['name'].str.contains(buyer_name)].head(1).index
        self.orderbook_buy_offers[stock].drop(indice_to_remove_buy, inplace=True)
        self.orderbook_sell_offers[stock].drop(indice_to_remove_sell, inplace=True)



    def create_candles(self):
        for stock in self.list_stocks:
            if len(self.transaction_list_one_day[stock].index)>0:
                open = self.transaction_list_one_day[stock]["price"].iloc[-1]
                close = self.transaction_list_one_day[stock]["price"].iloc[-1]
                high = self.transaction_list_one_day[stock]["price"].max()
                low = self.transaction_list_one_day[stock]["price"].min()
                new_data = pd.DataFrame({"Close": close, "Open": open, "High": high, "Low": low}, index=[0])
                self.stock_candles[stock] = pd.concat([self.stock_candles[stock], new_data], ignore_index=True)
                self.transaction_list_one_day[stock].drop(self.transaction_list_one_day[stock].index, inplace=True)
                print(f'Today transactions happened for {stock}')

            else:
                print(f"No Transactions today for stock {stock}! Creating artificial data!")
                mean = (self.stock_candles[stock].at[self.stock_candles[stock].index[-1], "Low"] + self.stock_candles[stock].at[self.stock_candles[stock].index[-1], "High"]) / 2
                var = self.stock_candles[stock]['Close'].rolling(10).std().mean()
                random_price_data = np.random.normal(mean, var, 20)
                close = random_price_data[-1]
                open = random_price_data[0]
                low = min(random_price_data)
                high = max(random_price_data)
                new_data = pd.DataFrame({"Close": close, "Open": open, "High": high, "Low": low}, index=[0])
                #print(new_data)
                self.stock_candles[stock] = pd.concat([self.stock_candles[stock], new_data], ignore_index=True)
                self.transaction_list_one_day[stock].reset_index()

    def push_opinions(self,jid,opinion,weight):
        self.stock_opinions[jid] = opinion*weight

    def get_stock_reputation(self):
        self.stock_reputation = np.zeros(len(self.list_stocks))
        for jid in self.list_investors:
            self.stock_reputation += self.stock_opinions[jid]
        self.stock_reputation = self.stock_reputation/np.sum(self.stock_reputation)
        print(self.stock_reputation)
        self.stock_reputation_history.append(self.stock_reputation.tolist())

    def data_visualization(self):
        x = np.arange(0,len(self.stock_reputation_history))
        y = list(map(list, zip(*self.stock_reputation_history)))
        plt.stackplot(x, y, labels=self.list_stocks)
        plt.legend()
        plt.show()







