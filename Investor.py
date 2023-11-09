import asyncio
import io

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import spade
import talib as tl
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import warnings
import Strategies_classes
import Strategies

class Investor(Agent):

    def __init__(self,jid,password,strategy):
        super().__init__(jid, password)
        self.strategy = strategy
    class InvestBehav(CyclicBehaviour):
        async def on_start(self):
            print(f"Starting {self.agent.jid} behaviour . . .")
            self.money = 5000
            self.stock_count = 100
            self.count = 0
            self.stock_list = ["1"]
        async def run(self):
            # receive stockdata
            await self.stockdata_receive()
            # send orderbook entry
            await self.orderbook_send()
            # receive transactions done
            await self.transactions_process()

        async def stockdata_receive(self):
            stockdata = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if stockdata:
                self.count += 1
                # print("Stockdata received, count {}".format(self.count))
                # Specify the file path where you want to save the text file
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=FutureWarning)
                    dataframe_stockdata = pd.read_json(stockdata.body, orient="split")

                    # instantiate strategy using strategy_num by setting it manually
                    strategy = f'strategy{self.agent.strategy}'
                    strategy_func = getattr(Strategies, strategy, None)
                    buy, sell = strategy_func(dataframe_stockdata)
                    orderbook_entry = {
                        "name": [self.agent.jid[0]],
                        "sell": [sell],
                        "buy": [buy]
                    }
                    self.orderbook_entry = pd.DataFrame(orderbook_entry)
                    # print(f'{self.agent.jid} is using {strategy}')
            else:
                print(f"{self.agent.jid} did not receive any stockdata after 10 seconds")
                self.kill()

        async def orderbook_send(self):
            # print("Sending Buy and Sell Offers")
            msg = Message(to="Orderbook@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = self.orderbook_entry.to_json(orient="split")  # Set the message content
            await self.send(msg)

        async def transactions_process(self):
            transactions = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if transactions:
                if "no" in transactions.body:
                    pass
                else:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=FutureWarning)
                        df_transactions = pd.read_json(transactions.body, orient="split")
                    buys = df_transactions['buyer'].str.contains(str(self.agent.jid[0]))
                    sells = df_transactions['seller'].str.contains(str(self.agent.jid[0]))
                    for money in df_transactions["price"][buys]:
                        self.money -= money
                        print("Agent" + str(self.agent.jid[0]) + "has" + str(self.money))
                    for money in df_transactions["price"][sells]:
                        self.money += money
                        print("Agent" + str(self.agent.jid[0]) + "has" + str(self.money))
    async def setup(self):
        print(f"{self.jid} started . . .")
        b = self.InvestBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)
