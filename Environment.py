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
    def __init__(self, list_stocks,num_investors):
        self.list_stocks = list_stocks
        self.investor_list = [f"investor{i}"for i in range(1,num_investors+1)]
        self.stock_candles = {}
        self.orderbook_sell_offers = {}
        self.orderbook_buy_offers = {}
        self.transaction_list_one_day = {}
        self.security_register = {}
        for stock in self.list_stocks:
            self.stock_candles[stock] = pd.read_csv('archive/Stocks/{}'.format(stock))[:52]
            self.orderbook_sell_offers[stock] =  pd.DataFrame(columns=["name", "sell"])
            self.orderbook_buy_offers[stock] =  pd.DataFrame(columns=["name", "buy"])
            self.transaction_list_one_day[stock] = pd.DataFrame(columns=["buyer", "seller","price"])
            self.security_register[stock] = pd.DataFrame(columns=["owner", "quantity"])


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

        if buyer not in self.security_register[stock].index:
            self.security_register[stock] = self.security_register[stock].append(
                pd.DataFrame({"quantity": [0]}, index=[buyer]))

        if seller not in self.security_register[stock].index:
            self.security_register[stock] = self.security_register[stock].append(
                pd.DataFrame({"quantity": [0]}, index=[seller]))

        self.security_register[stock].at[f'{buyer}','quantity'] += 1
        self.security_register[stock].at[f'{seller}', 'quantity'] -= 1

        print(self.security_register[stock])

        #Update orderbook
        self.transaction_list_one_day[stock] = pd.concat([self.transaction_list_one_day[stock], transaction], ignore_index=True)
        indice_to_remove_sell = self.orderbook_sell_offers[stock][self.orderbook_sell_offers[stock]['name'].str.contains(seller_name)].head(1).index
        indice_to_remove_buy = self.orderbook_buy_offers[stock][self.orderbook_buy_offers[stock]['name'].str.contains(buyer_name)].head(1).index
        self.orderbook_buy_offers[stock].drop(indice_to_remove_buy, inplace=True)
        self.orderbook_sell_offers[stock].drop(indice_to_remove_sell, inplace=True)



    def create_candles(self):
        for stock in self.list_stocks:
            if len(self.transaction_list_one_day)>0:
                open = self.transaction_list_one_day[stock]["price"].to_list[0]
                close = self.transaction_list_one_day[stock]["price"].to_list[-1]
                high = max(self.transaction_list_one_day[stock]["price"].to_list)
                low = min(self.transaction_list_one_day[stock]["price"].to_list)
                new_data = pd.DataFrame({"Close": close, "Open": open, "High": high, "Low": low}, index=[0])
                self.stock_candles[stock] = pd.concat([self.stock_candles[stock], new_data], ignore_index=True)
                self.transaction_list_one_day[stock] = pd.DataFrame(columns=["buyer", "seller","price"])

            else:
                print(f"No Transactions tody for stock {stock}! Creating artificial data!")
                mean = (self.stock_candles[stock].at[self.stock_candles[stock].index[-1], "Low"] + self.stock_candles[stock].at[
                    self.stock_candles[stock].index[-1], "High"]) / 2
                var = self.stock_candles[stock]['Close'].rolling(10).std().mean()
                random_price_data = np.random.normal(mean, var, 20)
                close = random_price_data[-1]
                open = random_price_data[0]
                low = random_price_data.min()
                high = random_price_data.max()
                new_data = pd.DataFrame({"Close": close, "Open": open, "High": high, "Low": low}, index=[0])
                self.stock_candles[stock] = pd.concat([self.stock_candles[stock], new_data], ignore_index=True)



list_stocks = ["zoes.us.txt"]
environment = Environment(list_stocks)
