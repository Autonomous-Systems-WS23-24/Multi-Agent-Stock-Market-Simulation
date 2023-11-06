import asyncio
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import spade
import talib as tl
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import json


class Orderbook(Agent):
    class OrderbookBehav(CyclicBehaviour):
        async def on_start(self):
            self.list_stocks = ["zoes.us.txt"]
            print("Creating Stockmarket Data . . .")
            for stock in self.list_stocks:
               self.stock_data = pd.read_csv('archive/Stocks/{}'.format(stock))
               self.stock_data = stock_cue_calc(self.stock_data)[100:102]
               print("calculation of cues completed!")
        async def run(self):
            print("Contacting Traders")
            self.investor_list = ["admin"]
            for investor in self.investor_list:
                msg = Message(to="{}@localhost".format(investor))  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.body = self.stock_data.to_json(orient="split")  # Set the message content
                await self.send(msg)
            print("Sent stockdata to traders!")

            #msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            #if msg:
            #    print("Message received with content: {}".format(msg.body))
            #else:
            #    print("Did not received any message after 10 seconds")

            # stop agent from behaviour
            await asyncio.sleep(1)

    async def setup(self):
        print("Agent starting . . .")
        template = Template()
        template.set_metadata("performative", "inform")
        b = self.OrderbookBehav()
        self.add_behaviour(b, template)


def stock_cue_calc(stock_data):
    # Calculate 52-day moving average
    stock_data['52-day MA'] = tl.MA(stock_data['Close'], timeperiod=52, matype=0)
    # Calculate 26-day moving average
    stock_data['26-day MA'] = tl.MA(stock_data['Close'], timeperiod=26, matype=0)
    # Calculate Relative Strength Index (RSI)
    stock_data['RSI'] = tl.RSI(stock_data['Close'], timeperiod=14)
    # Calculate Market Index and its slope
    stock_data['Market Index'] = (stock_data['High'] + stock_data['Low']) / 2
    stock_data['Market Index Slope'] = np.gradient(stock_data['Market Index'])
    # Calculate Market Level - Index Average
    market_index_average = stock_data['Market Index'].mean()
    stock_data['Market Level - Index Average'] = market_index_average
    # Calculate Market Index Acceleration
    stock_data['Market Index Acceleration'] = np.gradient(stock_data['Market Index Slope'])
    # Calculate MACD
    stock_data['MACD'], stock_data['Signal'], _ = tl.MACD(stock_data['Close'], fastperiod=12, slowperiod=26,
                                                             signalperiod=9)
    # Calcuate Stochastic Oscillator
    stock_data['K'], stock_data['D'] = tl.STOCH(stock_data['High'], stock_data['Low'], stock_data['Close'],
                                                   fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3,
                                                   slowd_matype=0)
    return stock_data


async def main():
    dummy = Orderbook("Orderbook@localhost", "1234")
    await dummy.start()
    print("DummyAgent started. Check its console to see the output.")

    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(dummy)

if __name__ == "__main__":
   spade.run(main())
