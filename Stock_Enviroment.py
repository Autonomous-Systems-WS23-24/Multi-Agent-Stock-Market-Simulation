import asyncio
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import spade
import talib as tl
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
import Orderbook
import Investor

class Stockmarket(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting Stock Market . . .")
            self.df = stock_cue_calc(pd.read_csv('archive/Stocks/zoes.us.txt'))
            self.counter = 0
        async def run(self):
            print("Day: {}".format(self.counter))
            self.stockprize = self.df["Open"][self.counter]
            print(self.stockprize)
            self.counter += 1
            await asyncio.sleep(1)

    async def setup(self):
        print("Agent starting . . .")
        b = self.MyBehav()
        self.add_behaviour(b)


async def main():
    Agent_Orderbook = Orderbook.Orderbook("Orderbook@localhost", "1234")
    Agent_Investor = Investor.Investor("admin@localhost", "1234")
    await Agent_Investor.start()
    await Agent_Orderbook.start()
    print("Orderbook is available. Check its console to see the output.")
    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(Orderbook)
    await wait_until_finished(Investor)



if __name__ == "__main__":
    spade.run(main())