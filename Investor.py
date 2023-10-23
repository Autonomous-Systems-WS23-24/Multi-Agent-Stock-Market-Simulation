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


class Investor(Agent):
    class InvestBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting behaviour . . .")
            self.money = 5000
            self.trade_condition = False
            self.count = 0
        async def run(self):
            stockdata = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if stockdata:
                self.count += 1
                print("Stockdata received, count {}".format(self.count))
                print(stockdata.body)
                # Specify the file path where you want to save the text file
                self.dataframe_stockdata = pd.read_csv(io.StringIO(stockdata.body), sep='\s+')
                print(self.dataframe_stockdata)
                print(self.dataframe_stockdata.shape)
                print("this was received")
            else:
                print("Did not received any stockdata after 10 seconds")

            # stop agent from behaviour
            await asyncio.sleep(1)
            #buy_prices = calculate_buy_prices(stock_data)
            #sell_prices = calculate_sell_prices(stock_data)
            #orderbook_msg = [buy_prices,sell_prices]
            #print("Sending Buy and Sell Offers")
            #msg = Message(to="Orderbook@localhost")  # Instantiate the message
            #msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            #msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            #msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            #msg.body = orderbook_msg  # Set the message content
            #await self.send(msg)

            #print("Message sent!")

            # set exit_code for the behaviour
            #self.exit_code = "Job Finished!"

            # stop agent from behaviour
            #await self.agent.stop()
        async def calculate_buy_prices(stock_data):
            pass

        async def calculate_sell_prices(stock_data):
            pass


    async def setup(self):
        print("Investor started")
        b = self.InvestBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)
