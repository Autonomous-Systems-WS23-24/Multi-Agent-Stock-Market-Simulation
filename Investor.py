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
import Strategies

class Investor(Agent):
    class InvestBehav(CyclicBehaviour):
        async def on_start(self):
            print(f"Starting {self.agent.jid} behaviour . . .")
            self.money = 5000
            self.trade_condition = False
            self.count = 0
            self.stock_list = ["1"]
        async def run(self):
            stockdata = await self.receive(timeout=50)  # wait for a message for 10 seconds
            if stockdata:
                self.count += 1
                #print("Stockdata received, count {}".format(self.count))
                # Specify the file path where you want to save the text file
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=FutureWarning)
                    self.dataframe_stockdata = pd.read_json(stockdata.body,orient="split")
                    self.offers = self.agent.strategy(self.dataframe_stockdata)
                    #print(self.offers)
            else:
                print("Did not received any stockdata after 10 seconds")
                self.kill()


            #print("Sending Buy and Sell Offers")
            msg = Message(to="Orderbook@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = self.offers.to_json(orient="split")  # Set the message content
            await self.send(msg)


    def strategy(self, dataframe_stockdata):
        buy_price, sell_price = Strategies.strategy_one(dataframe_stockdata)
        #print(f'{self.jid} wants to sell for {self.sell_price} and buy for {self.buy_price}')
        orderbook_entry = {
            "name": [self.jid[0]],
            "sell": [sell_price],
            "buy": [buy_price]
        }
        return pd.DataFrame(orderbook_entry)#,columns=["name","sell","buy"])

    async def setup(self):
        print(f"{self.jid} started . . .")
        b = self.InvestBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)
