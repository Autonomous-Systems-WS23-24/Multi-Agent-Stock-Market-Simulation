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
    def __init__(self, list_stocks):
        self.list_stocks = list_stocks
        self.stock_candles = {}
        self.orderbook_sell_offers = {}
        self.orderbook_buy_offers = {}
        self.transaction_list_one_day = {}
        for stock in self.list_stocks:
            self.stock_candles[f'{stock}'] = pd.read_csv('archive/Stocks/{}'.format(stock))[:52]
            self.orderbook_sell_offers[f"{stock}"] = pd.DataFrame(columns=["name", "sell"])
            self.orderbook_buy_offers[f"{stock}"] = pd.DataFrame(columns=["name", "buy"])
            self.transaction_list_one_day[f"{stock}"] = []

    def append_daily_transaction(self,stock_name):
        self.





list_stocks = ["zoes.us.txt"]
environment = Environment(list_stocks)
