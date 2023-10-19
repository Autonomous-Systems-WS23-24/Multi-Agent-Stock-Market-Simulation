import asyncio
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import spade
import talib as tl
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

class Investor(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting behaviour . . .")
            self.money = 5000
            self.trade_condition = False
        async def run(self):
            print("I have: {} Dollars".format(self.money))
            buy_prices = calculate_buy_prices(stock_data)
            sell_prices = calculate_sell_prices(stock_data)
            orderbook_msg = [buy_prices,sell_prices]
            print("Sending Buy and Sell Offers")
            msg = Message(to="Orderbook@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = orderbook_msg  # Set the message content
            await self.send(msg)

            print("Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

            # stop agent from behaviour
            await self.agent.stop()
        async def calculate_buy_prices(stock_data):
            pass

        async def calculate_sell_prices(stock_data):
            pass


    async def setup(self):
        print("Agent starting . . .")
        b = self.MyBehav()
        self.add_behaviour(b)
