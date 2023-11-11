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

    def __init__(self,jid,password,strategy,risk_factor):
        super().__init__(jid, password)
        self.strategy = strategy
        self.risk_factor = risk_factor
        self.networth_list = []
        self.money = 500
    class InvestBehav(CyclicBehaviour):
        async def on_start(self):
            print(f"Starting {self.agent.jid} behaviour . . .")
            self.stock_count = 25
            self.count = 0
            self.stock_list = ["1"]
        async def run(self):
            # receive stockdata
            await self.stockdata_receive()
            # send orderbook entry
            await self.orderbook_send()
            # receive transactions done
            await self.transactions_process()
            if self.count == 100:
                self.kill()

        async def on_end(self):
            x = np.arange(0,len(self.agent.networth_list))
            plt.xlabel("days")
            plt.ylabel("networth")
            plt.plot(x,self.agent.networth_list, label= f"Networth of {self.agent.jid[0]}")
            plt.ylim(0,max(self.agent.networth_list)*1.1)
            plt.legend()
            plt.show()

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
                    buy, sell = strategy_func(dataframe_stockdata,self.agent.risk_factor,self.agent.money)
                    orderbook_entry = {
                        "name": [self.agent.jid[0]],
                        "sell": [sell],
                        "buy": [buy]
                    }
                    self.orderbook_entry = pd.DataFrame(orderbook_entry)
                    current_networth = round(self.agent.money + self.stock_count*dataframe_stockdata.at[dataframe_stockdata.index[-1], 'Close'])
                    #print(f"{self.agent.jid} has {current_networth} Dollars of networth")
                    self.agent.networth_list.append(current_networth)
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
                    for price in df_transactions["price"][buys]:
                        self.agent.money -= price
                        self.stock_count += 1
                    for price in df_transactions["price"][sells]:
                        self.agent.money += price
                        self.stock_count -= 1
    async def setup(self):
        print(f"{self.jid} started . . .")
        b = self.InvestBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)
