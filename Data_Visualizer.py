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
import warnings


class Data_Visualizer(Agent):

    def __init__(self,jid,password,num_investors):
        super().__init__(jid, password)
        self.num_investors= num_investors
    class OrderbookBehav(CyclicBehaviour):
        async def on_start(self):


        async def run(self):



        async def send_stockdata(self):





    async def setup(self):
        print("Orderbook starting . . .")
        template = Template()
        template.set_metadata("performative", "inform")
        b = self.OrderbookBehav()
        self.add_behaviour(b, template)


async def main():
    dummy = Data_Visualizer("admin@localhost", "1234")
    await dummy.start()
    print("Data_Visualizer started. Check its console to see the output.")

    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(dummy)


if __name__ == "__main__":
    spade.run(main())
