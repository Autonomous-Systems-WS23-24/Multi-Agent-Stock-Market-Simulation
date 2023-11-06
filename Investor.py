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

class Investor(Agent):
    class InvestBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting behaviour . . .")
            self.money = 5000
            self.trade_condition = False
            self.count = 0
            self.stock_list = ["1"]
        async def run(self):
            stockdata = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if stockdata:
                self.count += 1
                #print("Stockdata received, count {}".format(self.count))
                # Specify the file path where you want to save the text file
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=FutureWarning)
                    self.dataframe_stockdata = pd.read_json(stockdata.body,orient="split")
                    self.offers = self.agent.lowrisk_strategy(self.dataframe_stockdata)
                    #print(self.offers)
            else:
                print("Did not received any stockdata after 10 seconds")


            #print("Sending Buy and Sell Offers")
            msg = Message(to="Orderbook@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = self.offers.to_json(orient="split")  # Set the message content
            await self.send(msg)


    def lowrisk_strategy(self, dataframe_stockdata):
        # The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements.
        # It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
        RSI_value = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'RSI']
        price_low = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Low']
        price_high = dataframe_stockdata.at[dataframe_stockdata.index[-1], 'High']
        price_mean = (price_low + price_high) / 2
        # moving average of last 52 days
        MA52 = dataframe_stockdata.at[dataframe_stockdata.index[-1], '52-day MA']
        #print(f'RSI: {RSI_value}', f'MA of alst 52 days: {MA52}')
        # buying when RSI value is lower than 35, and the mean price is 5 euro lower than the MA52. Buy the stock for the mean price
        if RSI_value < 35 and price_mean <= (MA52 - 5):
            buy_price = price_mean - 5
        else:
            buy_price = 0
        # selling when RSI value is higher than 40 or if the low price is 5 lower than MA52. Sell the stock for the mean price
        if RSI_value > 40 or price_low <= (MA52 - 5):
            sell_price = price_mean
        else:
            sell_price = 9999999999
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
